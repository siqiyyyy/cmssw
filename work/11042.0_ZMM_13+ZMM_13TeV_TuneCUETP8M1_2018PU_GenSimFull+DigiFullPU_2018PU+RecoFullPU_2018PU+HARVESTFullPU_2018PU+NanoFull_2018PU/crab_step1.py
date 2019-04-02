#crab config to submit jobs step1, step2, step3

from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.requestName = 'ZMM_GEN'
config.General.workArea = 'Crab3Area'

config.section_("JobType")
config.JobType.pluginName = 'PrivateMC'
#config.JobType.inputFiles = ['step2_DIGI_L1_DIGI2RAW_HLT_PU.py','step3_RAW2DIGI_L1Reco_RECO_RECOSIM_EI_PAT_VALIDATION_DQM_PU.py']
#config.JobType.disableAutomaticOutputCollection = True
#config.JobType.outputFiles = ['step3_inMINIAODSIM.root']
config.JobType.psetName = 'ZMM_13TeV_TuneCUETP8M1_cfi_GEN_SIM.py'
#config.JobType.allowUndistributedCMSSW = True

config.section_("Data")
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 200 #number of events per jobs
config.Data.totalUnits = 1000000 #number of event
config.Data.outLFNDirBase = '/store/user/syuan/ZMM_UPGRADE'  
config.Data.publication = True
config.Data.outputDatasetTag = 'QCD_FlatPT_2018_PU_HEDepth_GEN'
config.Data.outputPrimaryDataset = 'QCD_FlatPT_2018_PU_HEDepth_GEN'
#config.Data.lumiMask = ''

config.section_("Site")
config.Site.storageSite = 'T3_US_FNALLPC'
#config.Site.storageSite = 'T2_CH_CERN'
#config.Data.ignoreLocality=True
#config.Site.whitelist = ["T3_US*"]

