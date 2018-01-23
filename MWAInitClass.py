import argparse
import os
import ibcommon.parse as ib_parse
import MWAdbModelsClass as model

class MWAInit():

    mwa_bands = ['072-080','080-088','088-095','095-103','103-111',
                 '111-118','118-126','126-134','139-147','147-154',
                 '154-162','162-170','170-177','177-185','185-193',
                 '193-200','200-208','208-216','216-223','223-231',
                 '072-103','103-134','139-170','170-231']
    def __init__(self):
        self.set_args()
        self.set_table()
        self.set_objects()


    @property
    def table(self):
        return self.__table

    def set_table(self):
        tablemap = {'pne': model.PneDetected, 'snrs': model.Galacticsnrs}
        self.__table = tablemap[self.args.catalogue]
        return self

    @property
    def args(self):
        return self.__args

    def set_args(self):
        # parse inputs
        parser = argparse.ArgumentParser(description='Parse input for the photometry.')

        ## object selection
        parser.add_argument('--catalogue', '-c', action='store', choices=['pne', 'snrs'], required=True, type=str,
                            help="Choose between prepared catalogues.")
        parser.add_argument('--object', '-o', action='store', required=False, default='all', type=str,
                            help="Choose object by identification (all for all objects from the chosen cat).")
        parser.add_argument('--rewrite', '-r', action='store_true',
                            help="Rewrite over previous results TODO.")

        ## observation selection
        parser.add_argument('--week', '-w', action='store', choices=['2', '4'], required=False, type=str, default = 'all',
                            help="Select mosaics week (default all).")

        parser.add_argument('--band', '-b', action='store', choices=self.mwa_bands,
                            required=False, type=str, default = 'all', help="Select band (default all).")

        ## path selection
        parser.add_argument('--resultspath', '-i', action='store', required=True, type=str,
                            help="Full path to the folder where results will be stored.")
        parser.add_argument('--sourcepath', '-s', action='store', required=True, type=str,
                            help="Full path to the folder with input image(s).")
        parser.add_argument('--infile', '-f', action='store', required=False, default='default', type=str,
                            help="Input image.")
        parser.add_argument('--postfix', '-p', action='store', required=False, type=str, default="",
                            help="Postfix to be appended to resulting file names (default '').")

        ## photometry selection
        parser.add_argument('--blur', '-l', action='store', required=False, type=float, default=1.5,
                            help="Blur.")
        parser.add_argument('--annulus_in', '-q', action='store', required=False, type=float, default=1.5,
                            help="Annulus in factor.")
        parser.add_argument('--annulus_out', '-a', action='store', required=False, type=float, default=4.,
                            help="Annulus out factor.")
        parser.add_argument('--fix_offset', '-x', action='store_true',
                            help="Fix offset for imfit.")
        parser.add_argument('--conf_level', '-y', action='store', required=False, type=float, default=3.,
                            help="Confidence for aperture photometry (i.e. zero level = y * rms).")


        ## database selection
        parser.add_argument('--nowrite_db', '-d', action='store_true',
                            help="Do not write results to the database.")

        ## special
        parser.add_argument('--background_sub', '-e', action='store', required=False, type=str, default='default',
                            help="Name of the file with coordinates of background objects to subtract. ")

        ## special
        parser.add_argument('--select_data', '-g', action='store', choices=['mosaics', 'vointerface'], required=False,
                            type=str, default='mosaics',
                            help="Data source, local mosaics files or online vo interface (gleam-vo.icrar.org).")

        self.__args = parser.parse_args()


    @property
    def objects(self):
        return self.__objects

    def set_objects(self):
        objects = self.table.select(self.table.name,
                                    self.table.draj2000,
                                    self.table.ddecj2000,
                                    self.table.majdiam)

        if self.args.object != 'all':
            objects = objects.where(self.table.name == self.args.object)

        if objects.count() > 0:
            self.__objects = objects
            return True

        return False

    def extend_object(self,object):
        object.outfolder = self.set_outfolder(object)
        object.infolder = self.set_infolder(object)
        if object.majdiam == None:
            object.majdiam = 0
        return object

    def set_outfolder(self,object):
        outfolder = '{}{}/'.format(ib_parse.corrpath(self.args.resultspath), object.name)
        if not os.path.exists(outfolder):
            os.mkdir(outfolder)
        return outfolder

    def set_infolder(self,object):
        infolder = '{}{}/'.format(ib_parse.corrpath(self.args.sourcepath), object.name)
        if not os.path.exists(infolder):
            return False
        return infolder

    def select_mosaics(self,object):
        observations = model.MwaCutoutsModel.select().where(model.MwaCutoutsModel.name == object.name)
        ## extra selections
        ## week
        if self.args.week != 'all':
            observations = observations.where(model.MwaCutoutsModel.week == self.args.week)
        ## band
        if self.args.band != 'all':
            observations = observations.where(model.MwaCutoutsModel.band == self.args.band)

        if observations.count() > 0:
            return observations
        return False

    def write_to_mysql(self,results):
        if not self.args.nowrite_db:
            model.Photometry.create(**results)
        else:
            print "Writing to the db disabled."




