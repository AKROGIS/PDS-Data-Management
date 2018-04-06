import time, os, datetime, sys, logging, logging.handlers, shutil
import arcpy

########################## user defined functions ##############################

def getDatabaseItemCount(workspace):
    log = logging.getLogger("script_log")
    """returns the item count in provided database"""
    arcpy.env.workspace = workspace
    feature_classes = []
    log.info("Compiling a list of items in {0} and getting count.".format(workspace))
    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,datatype="Any",type="Any"):
        for filename in filenames:
            feature_classes.append(os.path.join(dirpath, filename))
    log.info("There are a total of {0} items in the database".format(len(feature_classes)))
    return feature_classes, len(feature_classes)

def replicateDatabase(dbConnection, targetGDB):
    log = logging.getLogger("script_log")
    startTime = time.time()

    if arcpy.Exists(dbConnection):
        featSDE,cntSDE = getDatabaseItemCount(dbConnection)
        log.info("Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE))
        if arcpy.Exists(targetGDB):
            featGDB,cntGDB = getDatabaseItemCount(targetGDB)
            log.info("Old Target Geodatabase: %s -- Feature Count: %s" %(targetGDB, cntGDB))
            try:
                shutil.rmtree(targetGDB)
                log.info("Deleted Old %s" %(os.path.split(targetGDB)[-1]))
            except Exception as e:
                log.error(e)

        GDB_Path, GDB_Name = os.path.split(targetGDB)
        log.info("Now Creating New %s" %(GDB_Name))
        arcpy.CreateFileGDB_management(GDB_Path, GDB_Name)

        arcpy.env.workspace = dbConnection

        try:
            datasetList = [arcpy.Describe(a).name for a in arcpy.ListDatasets()]
        except Exception, e:
            datasetList = []
            log.error(e)
        try:
            featureClasses = [arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()]
        except Exception, e:
            featureClasses = []
            log.error(e)
        try:
            tables = [arcpy.Describe(a).name for a in arcpy.ListTables()]
        except Exception, e:
            tables = []
            log.error(e)

        #Compiles a list of the previous three lists to iterate over
        allDbData = datasetList + featureClasses + tables

        for sourcePath in allDbData:
            targetName = sourcePath.split('.')[-1]
            targetPath = os.path.join(targetGDB, targetName)
            if not arcpy.Exists(targetPath):
                try:
                    log.info("Atempting to Copy %s to %s" %(targetName, targetPath))
                    arcpy.Copy_management(sourcePath, targetPath)
                    log.info("Finished copying %s to %s" %(targetName, targetPath))
                except Exception as e:
                    log.error("Unable to copy %s to %s" %(targetName, targetPath))
                    log.error(e)
            else:
                log.warning("%s already exists....skipping....." %(targetName))

        featGDB,cntGDB = getDatabaseItemCount(targetGDB)
        log.info("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))

    else:
        log.warning("{0} does not exist or is not supported! \
        Please check the database path and try again.".format(dbConnection))

#####################################################################################

def formatTime(x):
    minutes, seconds_rem = divmod(x, 60)
    if minutes >= 60:
        hours, minutes_rem = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
    else:
        minutes, seconds_rem = divmod(x, 60)
        return "00:%02d:%02d" % (minutes, seconds_rem)

if __name__ == "__main__":
    startTime = time.time()
    now = datetime.datetime.now()

    ############################### user variables #################################
    '''change these variables to the location of the database being copied, the target
    database location and where you want the log to be stored'''

    logPath = ""  # No path will put it in the current directory (likely the script directory)
    databaseConnection = r"Database Connections\inpakrovmais - facilities as DomainUser.sde"
    targetGDB = r"c:\tmp\fmss\akr_facility_new.gdb"   # must be a full path

    ############################### logging items ###################################
    # Make a global logging object.
    logName = os.path.join(logPath,(now.strftime("%Y-%m-%d_%H-%M.log")))

    log = logging.getLogger("script_log")
    log.setLevel(logging.INFO)

    h1 = logging.FileHandler(logName)
    h2 = logging.StreamHandler()

    f = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(lineno)d] - %(message)s",'%m/%d/%Y %I:%M:%S %p')

    h1.setFormatter(f)
    h2.setFormatter(f)

    h1.setLevel(logging.INFO)
    h2.setLevel(logging.INFO)

    log.addHandler(h1)
    log.addHandler(h2)

    log.info('Script: {0}'.format(os.path.basename(sys.argv[0])))

    try:
        ########################## function calls ######################################

        replicateDatabase(databaseConnection, targetGDB)

        ################################################################################
    except Exception, e:
        log.exception(e)

    totalTime = formatTime((time.time() - startTime))
    log.info('--------------------------------------------------')
    log.info("Script Completed After: {0}".format(totalTime))
    log.info('--------------------------------------------------')
