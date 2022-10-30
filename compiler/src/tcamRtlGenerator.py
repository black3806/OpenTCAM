import logging
import yaml
import json
import sys
import os
import re

# ===========================================================================================
# ======================================= Begin Class =======================================
# ===========================================================================================

class TcamRtlWrapperGenerator:
    # * ----------------------------------------------------------------- Variables
    def __init__(self):
        # * ------------------- public vars
        self.prjWorkDir = str()
        self.tcamMemWrapperConfigsFilePath  = str()
        self.tcamMemWrapperConfigsFileName  = str()
        self.tcamMemWrapperRTLFolderPath    = str()
        self.tcamMemWrapperRTLFilePath      = str()

        # * ------------------- protected vars
        self._currConfig            = dict()
        self._tcamMemWrapperConfigs = dict()
        self._topWrapperFileName    = str()

        # * ------------------- private vars
        self.__tcamRtlWrapLine  = list()
        # self.__inputWMask       = int()
        # self.__inputAddress     = int()
        # self.__outputReadData   = int()
        # self.__blockSelect      = int()
        
        # * logging config
        logging.basicConfig(level=logging.DEBUG, filename='./logs/TcamRtlWrapperGenerator.log',
                            format='%(asctime)s | %(filename)s | %(funcName)s | %(levelname)s | %(lineno)d | %(message)s')
    
    
    # * ----------------------------------------------------------------- Functions
    def getPrjDir(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        self.prjWorkDir=os.getcwd()
        logging.info('Project working dir: {:<s}'.format(self.prjWorkDir))
        printVerbose(verbose,'Project working dir: {:<s}'.format(self.prjWorkDir))
        return self.prjWorkDir
    
    
    def getYAMLFilePath(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * get tcamTables config file path
        tempPath = os.path.join(self.prjWorkDir,'compiler/configs/tcamMemWrapper.yaml')
        if os.path.isfile(tempPath) is True:
            self.tcamMemWrapperConfigsFilePath = tempPath
            self.tcamMemWrapperConfigsFileName = os.path.basename(tempPath)
            logging.info('"FOUND": TCAM memory wrapper config file path: {:<s}'.format(self.tcamMemWrapperConfigsFilePath))
            printVerbose(verbose,'"FOUND": TCAM memory wrapper config file path: {:<s}'.format(self.tcamMemWrapperConfigsFileName))
            return self.tcamMemWrapperConfigsFilePath
        else:
            logging.error('"NOT FOUND": TCAM memory wrapper config file path: {:<s}'.format(self.tcamMemWrapperConfigsFilePath))
            sys.exit('"NOT FOUND": TCAM memory wrapper config file path: {:<s}'.format(self.tcamMemWrapperConfigsFileName))
    
    
    def readYAML(self,filePath,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        with open(filePath) as file:
            self._tcamMemWrapperConfigs=yaml.full_load(file)
        # print(json.dumps(self._tcamMemWrapperConfigs, indent=4))
        # print(yaml.dump(self._tcamMemWrapperConfigs, sort_keys=False, default_flow_style=False))
        logging.info('Read TCAM memory wrapper config file: {:<s}'.format(self.tcamMemWrapperConfigsFilePath))
        printVerbose(verbose,'Read TCAM memory wrapper config file: {:<s}'.format(self.tcamMemWrapperConfigsFileName))
        return self._tcamMemWrapperConfigs
    
    
    def printYAML(self,debug):
        """
        what does this func do ?
        input args:
        return val:
        """
        printDebug(debug, 'Printing TCAM memory wrapper configs')
        print(json.dumps(self._tcamMemWrapperConfigs, indent=4))
        # print(yaml.dump(self._tcamMemWrapperConfigs, sort_keys=False, default_flow_style=False))
        logging.info('Printed TCAM memory wrapper configs')
    
    
    def getTCAMWrapperConfig(self, tcamWrapConfig):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * look for specific tcam config in compiler/configs/tcamTables.yaml
        if tcamWrapConfig in self._tcamMemWrapperConfigs.keys():
            self._currConfig = self._tcamMemWrapperConfigs[tcamWrapConfig]
            # * save tcam config vars
            # self.__inputWMask       = self._currConfig['inputWMask']
            # self.__inputAddress     = self._currConfig['inputAddress']
            # self.__outputReadData   = self._currConfig['outputReadData']
            # self.__blockSelect      = self._currConfig['blockSelect']
            # * print specific tcam config
            # print(self._currConfig)
            logging.info('"FOUND" Required TCAM Memory Wrapper Config [{:<s}]'.format(tcamWrapConfig))
            print('\n"FOUND" Required TCAM Memory Wrapper Config [{:<s}]'.format(tcamWrapConfig))
            logging.info('TCAM Memory Wrapper Config Data [{:<s}] = {}'.format(tcamWrapConfig, self._currConfig))
            return self._currConfig
        else:
            logging.error('"NOT FOUND": TCAM Memory Wrapper Config [{:<s}]'.format(tcamWrapConfig))
            sys.exit('"NOT FOUND": Required TCAM Memory Wrapper Config [{:<s}]'.format(tcamWrapConfig))
    
    
    def createWrapConfigDir(self, tcamWrapConfig, verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        self.tcamMemWrapperRTLFolderPath = os.path.join(self.prjWorkDir, 'tcam_mem_rtl', tcamWrapConfig)
        if os.path.exists(self.tcamMemWrapperRTLFolderPath) is False:
            os.makedirs(self.tcamMemWrapperRTLFolderPath)
            logging.info('Created TCAM memory "{:<s}" RTL folder: {:<s}'.format(tcamWrapConfig, self.tcamMemWrapperRTLFolderPath))
            printVerbose(verbose, 'Created TCAM memory "{:<s}" RTL folder: {:<s}'.format(tcamWrapConfig, self.tcamMemWrapperRTLFolderPath))
    
    
    def createWrapConfigFile(self, tcamWrapConfig):
        """
        what does this func do ?
        input args:
        return val:
        """
        self._topWrapperFileName = 'top_' + str(tcamWrapConfig).replace('MemWrapper_','_mem_') + '.sv'
        self.tcamMemWrapperRTLFilePath = os.path.join(self.tcamMemWrapperRTLFolderPath, self._topWrapperFileName)
        logging.info('Created TCAM memory "{:<s}" wrapper: {:<s}'.format(tcamWrapConfig, self.tcamMemWrapperRTLFilePath))
    
    
    def generateWrapper(self):
        with open(self.tcamMemWrapperRTLFilePath, 'w') as file1:
            for line in self.__tcamRtlWrapLine:
                file1.write(line)
        file1.close()
    
    
    def writeTimeScale(self, timeUnit, timePrecision):
        tempLine = '`timescale ' + str(timeUnit).replace(' ','') + '/' + str(timePrecision).replace(' ','')
        self.__tcamRtlWrapLine.append(tempLine)
        logging.info('Added timescale in: {:<s}'.format(self._topWrapperFileName))





# ===========================================================================================
# ======================================== End Class ========================================
# ===========================================================================================

def printVerbose(verbose,msg):
    if verbose:
        print(str(msg))

def printDebug(debug,msg):
    if debug:
        print(str(msg))
