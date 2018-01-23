import os
import sys
import shutil
from math import isnan, floor

import numpy as np
from astropy import units as u
from astropy.coordinates import Longitude, Latitude
from casa import importfits, imfit, imhead, imstat, exportfits, immath

import ibplotting.plotlibs as ibplot
from qb_common import parse, dicts, strings


class MWAPhotometry:
    __fit_results = {}
    __fitresults = {}
    __blobpars = {}
    __blobstats = {}
    __bckgstats = {}
    __aprtrstats = {}

    def __init__(self, inobject, observation, args):
        ## load object setup
        self.obj = inobject
        ## load observation setup
        self.obs = observation
        ## load input arguments
        self.args = args

    ## getter and setter for blobcat parameters
    @property
    def blobpars(self):
        return self.__blobpars

    ## getter and setter for background statistics
    @property
    def bckgstats(self):
        return self.__bckgstats

    def set_bckgstats(self):
        ## preliminary stats
        prel_stats = self.get_statistics(in_image=self.obs.files['imfile'],
                                         in_region=self.obs.pars['region_annulus'])
        ## find min and max for noise
        top_signal = prel_stats['mean'] + 5 * prel_stats['sigma']
        low_signal = prel_stats['mean'] - 5 * prel_stats['sigma']
        ## mask outside noise
        mask = "{}<'{}' && '{}'<{}".format(low_signal, self.obs.files['imfile'], self.obs.files['imfile'], top_signal)
        self.__bckgstats = self.get_statistics(in_image=self.obs.files['imfile'],
                                               in_region=self.obs.pars['region_annulus'],
                                               mask=mask)

    ## getter and setter for aperture photometry
    @property
    def aprtrstats(self):
        return self.__aprtrstats

    ## getter and setter for blob photometry
    @property
    def blobstats(self):
        return self.__blobstats

    def aperture_phot(self, image, zerolevel, prefix=""):
        results = {}
        mask = "'{}'>{}".format(image, zerolevel)
        tmp_aprtrstats = self.get_statistics(image,
                                             self.obs.pars['region_fit'],
                                             mask)
        if not tmp_aprtrstats:
            return False
        if tmp_aprtrstats['npts'].size != 0 and tmp_aprtrstats['npts'] > 0:
            ## rename keys
            if prefix != "":
                prefix = "{}_".format(prefix)
            for i in tmp_aprtrstats:
                results["{}{}".format(prefix, i)] = tmp_aprtrstats[i]
        return results

    ## get statistics in defined region
    ## https://casa.nrao.edu/casadocs-devel/stable/global-task-list/task_imstat/about
    @staticmethod
    def get_statistics(in_image, in_region, mask=''):
        tmp_stats = imstat(imagename=in_image,
                           region=in_region,
                           mask=mask)
        res = {}
        ## convert single vectors (i.e. [4]) into values
        if not tmp_stats:
            return False
        for i in tmp_stats:
            res[i] = parse.singlevec(tmp_stats[i])
        return res

    ## getter for fit results
    @property
    def fit_res(self):
        return self.__fitresults

    ## run source fitting
    ## https://casa.nrao.edu/casadocs-devel/stable/global-task-list/task_imfit/about
    def do_fit(self):
        fitinput = {
            'imagename':self.obs.files['imfile'],
            'region':self.obs.pars['region_fit'],
            'logfile':self.obs.files['logtable'],
            'dooff':True,
            'offset':self.bckgstats['mean'],
            'fixoffset':self.args.fix_offset,
            'summary':self.obs.files['summaryfile'],
            'model':self.obs.files['modelfile']}
        tmpfitresults = imfit(**fitinput)
        try:
            for i in tmpfitresults:
                self.__fitresults[i] = parse.singlevec(tmpfitresults[i])
        except:
            print 'nans in fit results'

    ## subtract background object
    def bckgsrc_fit(self, imfile, bckg_region, out_file):
        imfit(
            imagename=imfile,
            region=bckg_region,
            dooff=True,
            offset=self.bckgstats['mean'],
            fixoffset=self.args.fix_offset,
            model=out_file)

    def subtract_bckgs(self):
        for bckg in self.obs.bckg:
            tmpimfile = "tmps/tmpimfile_{}.im".format(strings.id_generator())
            tmpmodel = "tmps/tmpmodelfile_{}.im".format(strings.id_generator())
            shutil.move(self.obs.files['imfile'], tmpimfile)
            bckg_reg = 'circle[[{}deg,{}deg],{}arcsec]'.format(bckg[0], bckg[1], self.obs.pars['use_bmaj'])
            self.bckgsrc_fit(tmpimfile, bckg_reg, tmpmodel)
            immath([tmpimfile, tmpmodel],
                   'evalexpr', self.obs.files['imfile'], expr='IM0-IM1')
            shutil.rmtree(tmpmodel)
            shutil.rmtree(tmpimfile)
            ## do background statistics again
            self.set_bckgstats()

    ## mask all pixels bellow given level
    def make_masked(self):
        try:
            expression = 'iif(IM0<{},0,IM0)'.format(self.bckgstats['rms'] * self.args.conf_level)
            immath(imagename=[self.obs.files['imfits']], mode='evalexpr', outfile=self.obs.files['maskedimage'],
                   expr=expression)
            imhead(self.obs.files['maskedimage'], mode='put', hdkey='BUNIT', hdvalue='Jy/beam')
            return True
        except:
            return False

    ## getter for attribute converged (boolean)
    @property
    def converged(self):
        return self.fit_res['converged']

    def photometry(self):
        ## get statistics in the annulus
        self.set_bckgstats()
        ## subtract backgrounds if any
        self.subtract_bckgs()
        ## make fits image from im
        exportfits(self.obs.files['imfile'], self.obs.files['imfits'])
        ## run source fitting
        self.do_fit()
        if self.converged:
            self.parse_fit()
        ## do aperture photometry
        if self.make_masked():
            self.__aprtrstats = self.aperture_phot(self.obs.files['maskedimage'], 0, "aprtr")
            self.make_masked_images()
        if self.blobit():
            self.__blobstats = self.aperture_phot(self.obs.files['maskedblobs'], 0, "blob")
            self.make_blob_images()

    ## results getter
    @property
    def results(self):
        return self.__fit_results

    ## parse fir results from imfit
    def parse_fit(self):

        imfit_out_component = self.fit_res['results']['component0']

        flux = imfit_out_component['flux']
        peak = imfit_out_component['peak']
        shape = imfit_out_component['shape']
        self.__fit_results = {
            'flux_err': flux['error'][0],
            'flux_unit': flux['unit'],
            'flux': flux['value'][0],
            'peak_err': peak['error'],
            'peak_unit': peak['unit'],
            'peak': peak['value'],
            'm0': shape['direction']['m0']['value'],
            'm1': shape['direction']['m1']['value'],
            'fit_posra': Longitude(shape['direction']['m0']['value'], u.rad).deg,
            'fit_posdec': Latitude(shape['direction']['m1']['value'], u.rad).deg,
            'off_lat': shape['direction']['error']['latitude']['value'],
            'off_lat_unit': shape['direction']['error']['latitude']['unit'],
            'off_long': shape['direction']['error']['longitude']['value'],
            'off_long_unit': shape['direction']['error']['longitude']['unit'],
            'maj_ax': shape['majoraxis']['value'],
            'maj_ax_unit': shape['majoraxis']['unit'],
            'maj_ax_err': shape['majoraxiserror']['value'],
            'maj_ax_err_unit': shape['majoraxiserror']['unit'],
            'min_ax': shape['minoraxis']['value'],
            'min_ax_unit': shape['minoraxis']['unit'],
            'min_ax_err': shape['minoraxiserror']['value'],
            'min_ax_err_unit': shape['minoraxiserror']['unit'],
            'pa': shape['positionangle']['value'],
            'pa_unit': shape['positionangle']['unit'],
            'pa_err': shape['positionangleerror']['value'],
            'pa_err_unit': shape['positionangleerror']['unit'],
            'type': shape['type'],
            'conv': parse.booltostring(self.fit_res['converged']),
            'ispoint': parse.booltostring(imfit_out_component['ispoint'])
        }
        checknas = ['flux_err', 'flux', 'peak_err', 'peak', 'maj_ax', 'maj_ax_err', 'min_ax', 'min_ax_err', 'pa',
                    'pa_err', 'off_lat', 'off_long']
        for checkna in checknas:
            if isnan(self.__fit_results[checkna]):
                del self.__fit_results[checkna]

    def parse_to_mysql(self):
        res = dicts.merge_dicts([
            self.obj._data,
            vars(self.args),
            self.obs.files,
            self.bckgstats,
            self.fit_res,
            self.obs.pars,
            self.results,
            self.aprtrstats,
            self.blobstats,
            self.blobpars,
            {'inimage':self.obs.inimage}
            ])
        return res


    ## apply blobcat algorithm to find extended emission
    ## see http://adsabs.harvard.edu/abs/2012MNRAS.425..979H
    ## script source: http://blobcat.sourceforge.net/
    def blobit(self):
        if not self.aprtrstats:
            return False
        blobpars = {
            'rmsval': self.bckgstats['rms'],
            'bmaj': self.obs.pars['use_bmaj'],
            'bmin': self.obs.pars['use_bmin'],
            'bpa': self.obs.pars['use_bpa'],
            'dSNR': self.aprtrstats['aprtr_median'] / self.bckgstats['rms'],
            'fSNR': self.aprtrstats['aprtr_q1'] / self.bckgstats['rms'],
            'minpix': int(floor(self.aprtrstats['aprtr_npts'] * 0.1)),
            'maxpix': int(floor(self.aprtrstats['aprtr_npts'] * 2.5)),
            'hfill': 999.
        }
        pars = ''
        for par in blobpars:
            pars = "{} --{}={}".format(pars, par, blobpars[par])
            self.__blobpars["blob_{}".format(par)] = blobpars[par]

        command = "code/blobcat.py {} --write {}".format(self.obs.files['imfits'], pars)
        os.system(command)
        if not os.path.exists(self.obs.files['imfit_blobs']):
            return False

        importfits(fitsimage=self.obs.files['imfit_blobs'], imagename=self.obs.files['imfile_blobs'])
        expression = 'iif(IM0<999,0,IM1)'
        immath(imagename=[self.obs.files['imfile_blobs'], self.obs.files['imfile']], mode='evalexpr',
               outfile=self.obs.files['maskedblobs'], expr=expression)
        exportfits(fitsimage=self.obs.files['maskedblobsfits'], imagename=self.obs.files['maskedblobs'])
        return True


    def make_fit_images(self):

        cont_levels = np.array([2., 3., 5., 8., 12., 17., 23.]) * (float(self.bckgstats['sigma'])) + self.bckgstats['rms']
        rms_levels = np.array([1.]) * float(self.bckgstats['rms'])

        fit_crosses = []
        if self.converged:
            fit_crosses = [[self.results['fit_posra'], self.results['fit_posdec'], self.obj.name]]
            immath([self.obs.files['imfile'], self.obs.files['modelfile']],
                   'evalexpr', self.obs.files['residualimage'], expr='IM0-IM1')
            exportfits(self.obs.files['residualimage'], self.obs.files['residualfits'])
            ibplot.photFigure(self.obs.files['residualfits'], self.obs.files['residualpngfile'],
                              self.obj.draj2000, self.obj.ddecj2000, self.obs.pars['annulus_in'] / 3600.,
                              self.obs.pars['annulus_out'] / 3600., self.obs.pars['radius'] / 3600.,
                              self.obj.majdiam / 3600., cont_levels, -1,
                              rLevels=rms_levels, crosses=fit_crosses, imsize=2. * self.obs.pars['annulus_out'] / 3600.)
            exportfits(self.obs.files['modelfile'], self.obs.files['modelfits'])

        ibplot.photFigure(self.obs.files['imfits'], self.obs.files['pngfile'],
                          self.obj.draj2000, self.obj.ddecj2000, self.obs.pars['annulus_in'] / 3600.,
                          self.obs.pars['annulus_out'] / 3600., self.obs.pars['radius'] / 3600.,
                          self.obj.majdiam / 3600., cont_levels, -1,
                          rLevels=rms_levels, crosses=fit_crosses, imsize=2. * self.obs.pars['annulus_out'] / 3600.)



        return True

    def make_masked_images(self):
        cont_levels = np.array([3., 5., 8., 12.]) * (float(self.bckgstats['sigma'])) + self.bckgstats['rms']
        rms_levels = np.array([1.]) * float(self.bckgstats['rms'])

        exportfits(fitsimage=self.obs.files['maskedfits'], imagename=self.obs.files['maskedimage'])

        ibplot.photFigure(self.obs.files['maskedfits'], self.obs.files['maskedpng'],
                          self.obj.draj2000, self.obj.ddecj2000, self.obs.pars['annulus_in'] / 3600.,
                          self.obs.pars['annulus_out'] / 3600., self.obs.pars['radius'] / 3600.,
                          self.obj.majdiam / 3600., cont_levels, -1,
                          valmin=1E-6,
                          valmax=self.bckgstats['rms'] * 5,
                          rLevels=rms_levels, imsize=1.2 * self.obs.pars['annulus_in'] / 3600.)


    def make_blob_images(self):
        cont_levels = np.array([1.]) * self.__blobpars['blob_dSNR'] * self.bckgstats['rms']
        rms_levels = np.array([1.]) * self.__blobpars['blob_fSNR'] * self.bckgstats['rms']
        ibplot.photFigure(self.obs.files['maskedblobsfits'], self.obs.files['maskedblobspng'],
                          self.obj.draj2000, self.obj.ddecj2000, self.obs.pars['annulus_in'] / 3600.,
                          self.obs.pars['annulus_out'] / 3600., self.obs.pars['radius'] / 3600.,
                          self.obj.majdiam / 3600., cont_levels, -1,
                          valmin=1E-6,
                          valmax=self.__blobpars['blob_dSNR'] * self.bckgstats['rms'] * 2,
                          rLevels=rms_levels, imsize=1.2 * self.obs.pars['annulus_in'] / 3600.)
