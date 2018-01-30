import os
from casa import importfits, imfit, imhead, imstat, exportfits, immath
import shutil
import sys
import csv
import MWAdbModelsClass as model

sys.path.insert(0, "/Users/ibojicic/PycharmProjects/gleamvo-client/")

class MWAObservation ():

    def __init__(self, object,args,data):
        self.files = None

        self.__object = object
        self.__args = args
        self.__data = data
        ## load mysql models

    ## remove previous observation results and files if rewrite flag
    def check_rewrite(self):
        ## check rewrite
        if not self.args.rewrite:
            return True
        ## if writing to db delete old mysql results
        if not self.args.nowrite_db:
            delres = model.Photometry.delete().where(
                (model.Photometry.name == self.object.name) &
                (model.Photometry.week == self.data.week) &
                (model.Photometry.band == self.data.band)
            )
            delres.execute()
        ## delete result files if they exits since casa doesn't allow overwriting
        for file in self.files:
            if os.path.isfile(self.files[file]):
                os.remove(self.files[file])
            elif os.path.isdir(self.files[file]):
                shutil.rmtree(self.files[file])


    def check_done(self):
        res = model.Photometry.select().\
            where((model.Photometry.name == self.object.name) &
                  (model.Photometry.week == self.data.week) &
                  (model.Photometry.band == self.data.band))
        return (not res.count() > 0) or self.args.nowrite_db


    @property
    def object(self):
        return self.__object

    @property
    def args(self):
        return self.__args

    @property
    def data(self):
        return self.__data

    def create_filename(ra, dec, ang_size, freq, error=False):
        """
        You can write your own create_filename function however you like
        Here is a dummy example
        """
        if (error):
            return "error_{0}_{1}_{2}_{3}.html".format(ra, dec, ang_size, freq)
        else:
            return "{0}_{1}_{2}_{3}.fits".format(ra, dec, ang_size, freq)



    def construct_file_name(self, folder, type, ext='fits'):
        widebands = ['072-103', '103-134', '139-170', '170-231']
        wideband = ""
        if self.data.band in widebands:
            wideband = 'wideband_'
        return '{}{}_{}mosaic_Week{}_{}MHz_{}{}.{}'.\
            format(folder, self.object.name, wideband, self.data.week, self.data.band, type, self.args.postfix, ext)


    def set_in_file(self):
        if self.data.out_vo_image is not None:
            self.inimage = "{}vo/{}".format(self.object.infolder,self.data.out_vo_image)
        elif self.data.corrmos == 'corr':
            if self.data.out_corr_image is not None:
                self.inimage = "{}corr/{}".format(self.object.infolder,self.data.out_corr_image)
            else:
                return False
        elif self.data.corrmos == 'mos':
            if self.data.out_mos_image is not None:
                self.inimage = "{}mos/{}".format(self.object.infolder,self.data.out_mos_image)
            else:
                return False

        return True

    def set_out_files(self):
        if self.files is None:
            self.files = {}

        outfiles = {'imfile':['input', 'im'],
                    'imfits':['imfit','fits'],
                    'imfit_blobs': ['imfit_blobs', 'fits'],
                    'imfile_blobs': ['imfit_blobs', 'im'],
                    'pngfile':['phot', 'png'],
                    'modelfile':['model','im'],
                    'modelfits':['model','fits'],
                    'logtable':['table','log'],
                    'residualimage':['residual', 'im'],
                    'residualfits':['residual', 'fits'],
                    'residualpngfile':['residual', 'png'],
                    'maskedimage': ['masked', 'im'],
                    'maskedblobs': ['maskedblobs', 'im'],
                    'maskedfits': ['masked', 'fits'],
                    'maskedblobsfits': ['maskedblobsfits', 'fits'],
                    'maskedblobspng': ['maskedblobs', 'png'],
                    'maskedpng': ['masked', 'png'],
                    'summaryfile':['summary', 'txt']
                    }


        for outf in outfiles:
            self.files[outf] = self.construct_file_name(self.object.outfolder, outfiles[outf][0],outfiles[outf][1])

        return True

    def create_imfile(self):
        if not os.path.exists(self.files['imfile']):
            importfits(fitsimage=self.inimage, imagename=self.files['imfile'])
            imhead(self.files['imfile'], mode='put', hdkey='BUNIT', hdvalue='Jy/beam')


    def parse_bckg_file(self):
        self.bckg = []
        bckfile = "regions/{}.reg".format(self.object.name)
        if os.path.exists(bckfile):
            with open(bckfile, 'rb') as f:
                reader = csv.reader(f,quoting=csv.QUOTE_NONNUMERIC)
                self.bckg = list(reader)

    def set_obs_pars(self):
        pars = {}
        pars['freqHz'] = int(imhead(imagename=self.files['imfile'], mode='get', hdkey='FREQ'))
        pars['band'] = self.data.band
        pars['week'] = self.data.week
        if self.data.BMAJ is None:
            return False
        pars['use_bmaj'], pars['use_bmin'], pars['use_bpa'], pars['use_blur'] = \
            3600. * self.data.BMAJ, 3600. * self.data.BMIN, self.data.BPA, self.data.BBLUR
        if pars['use_blur'] is None:
            pars['use_blur'] = 1.

        if pars['use_bmaj'] < 1.:
            pars['use_bmaj'] = float(imhead(imagename=self.files['imfile'], mode='get', hdkey='BMAJ')['value'])
            pars['use_bmin'] = float(imhead(imagename=self.files['imfile'], mode='get', hdkey='BMIN')['value'])
            pars['use_blur'] = self.args.blur

        if float(self.object.majdiam) / 2. < pars['use_bmaj'] / 2. * pars['use_blur']:
            pars['radius'] = pars['use_bmaj'] / 2. * pars['use_blur']
        else:
            pars['radius'] = float(self.object.majdiam) / 2.

        pars['annulus_in'] = pars['radius'] * self.args.annulus_in
        pars['annulus_out'] = pars['radius'] * self.args.annulus_out

        # define regions
        pars['region_fit'] = 'circle[[{}deg,{}deg],{}arcsec]'.format(self.object.draj2000, self.object.ddecj2000, pars['annulus_in'])
        pars['region_annulus'] = 'annulus[[{}deg,{}deg],[{}arcsec,{}arcsec]]'.format(self.object.draj2000, self.object.ddecj2000,
                                                                                     pars['annulus_in'],pars['annulus_out'])
        self.pars = pars
        return True

