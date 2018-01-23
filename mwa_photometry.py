from MWAInitClass import MWAInit
from MWAObservationClass import MWAObservation
from MWAPhotometryClass import MWAPhotometry

if __name__ == "__main__":

    mwa_photo = MWAInit()

    for object in mwa_photo.objects:

        object = mwa_photo.extend_object(object)
        observations = mwa_photo.select_mosaics(object)

        for obsdata in observations:
            obs = MWAObservation(object,mwa_photo.args,obsdata)
            if not obs.set_in_file():
                continue
            obs.set_out_files()
            obs.check_rewrite()
            if obs.check_done():
                obs.create_imfile()
                obs.parse_bckg_file()
                if not obs.set_obs_pars():
                    continue
                photo = MWAPhotometry(object,obs,mwa_photo.args)

                try:

                    photo.photometry()

                    photres = photo.parse_to_mysql()
                    photo.make_fit_images()

                    mwa_photo.write_to_mysql(photres)
                    print "finished observations"
                except:
                    print "photometry error"





