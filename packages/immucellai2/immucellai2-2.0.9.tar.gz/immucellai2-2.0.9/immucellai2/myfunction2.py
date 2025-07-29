#!/usr/bin/python3
from immucellai2.myclasses import CLASS_FOR_RUN
from immucellai2.myfunction3 import ObtainCellTypeCateogry
import pandas
import os
import re
import sys
import multiprocessing as mp
from importlib import resources

def SelectGeneForDeconvolution(DFReferenceProfile, FileCoveredGenes="", Method="UsedMarker"):
    print("Select the gene for the following deconvolution...")
    GeneUsedForDeconvolution = []
    DFReferenceProfileGenes = DFReferenceProfile.index.values
    if Method == "UsedMarker":
        if FileCoveredGenes == "":
            try:
                with resources.path("immucellai2.myconfig", "MarkerUsedDeconvolution.txt") as marker_path:
                    FileCoveredGenes = str(marker_path)
            except Exception as e:
                import os, sys, re
                script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                FileCoveredGenes = os.path.join(script_dir, "immucellai/myconfig/MarkerUsedDeconvolution.txt")
                print(f"[警告] 使用回退路径: {FileCoveredGenes}")
        try:
            GeneUsedForDeconvolution0 = pd.read_table(FileCoveredGenes, sep="\t", header=None).iloc[0].tolist()
            GeneUsedForDeconvolution = list(set(GeneUsedForDeconvolution0).intersection(set(DFReferenceProfileGenes)))
            print(f"成功读取 {len(gene_used)} 个标记基因")
        except FileNotFoundError:
            print(f"错误: 标记文件不存在 - {FileCoveredGenes}")
            print("请检查:")
            print("1. 包是否正确安装 (pip install --upgrade immucellai2)")
            print("2. 环境变量 IMMUCELLAI_CONFIG_DIR 是否设置")
            return []
        except Exception as e:
            print(f"读取文件时出错: {str(e)}")
            return [] 
    return GeneUsedForDeconvolution

def CelltypeCategoryCheck(FileCellTypeCategory = "", celltypelist = [] ):
   print("Check the Celltype covered by configfile")
   if FileCellTypeCategory == "":
      FileCellTypeCategory = Obtainmyconfigpath() + "Celltype.cateogory"
   obtaincontent = ObtainCellTypeCateogry(FileCellTypeCategory)
   Allcelltype = []
   for keyword, oneCellTypeNode in obtaincontent.items():
      Allcelltype += [ keyword ] + oneCellTypeNode["AlsoKnownAs"] + oneCellTypeNode["RelatedNode"]["HisChidNode"]
   for onecelltype in celltypelist:
      if onecelltype not in Allcelltype:
         raise ValueError( "EEROR: reference matrix celltpe'{0}' NOT IN configfile, please CHECK...".format(onecelltype))
   return FileCellTypeCategory
   
def InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio = "", ncelltype = 0):
   print("Check the celltype ratio initialization method...")
   if InitialCellTypeRatio[1] != "prior":
      return
   if FileInitialCellTypeRatio == "":
      FileInitialCellTypeRatio = Obtainmyconfigpath() + "myCellTypeRatio.initial"
   Expactedcelltypenum = (pandas.read(FileInitialCellTypeRatio, sep = "\t", header = 0, index_col = 0)).shape[1]
   if Expactedcelltypenum <1:
      raise ValueError("FAILED")
   elif Expactedcelltypenum in [ ncelltype, ncelltype -1 ]:
      return FileInitialCellTypeRatio
   else:
      InitialCellTypeRatio = 'randn'     

def PrepareData(FileReferenceProfile , 
   FileSampleExpressionProfile , 
   EnvironmentConfig = ("", "") ,
   FileCoveredGenes = "" ,
   FileCellTypeCategory = "" ,
   FileInitialCellTypeRatio = "" ,
   InitialCellTypeRatio = ('Normone', 'randn')):
   print("prepare for RunObject...")
   DFReferenceProfile0 = pandas.read_table(FileReferenceProfile, sep= "\t", header=0, index_col = 0)
   if DFReferenceProfile0.shape[1] < 2:
      print("warning: When open Reference File, might sep = ' ' not '\t'")
   print("celltype reference raw matrix:\n", DFReferenceProfile0.iloc[0:4, 0:4])
   ReferenceCelltype = {} 
   for oneCellType in DFReferenceProfile0.columns.values.tolist():
      numbertail = re.findall("\.[0-9]*$", oneCellType)
      oneCellType0 = oneCellType
      if numbertail != []: oneCellType = oneCellType[:-len(numbertail)]
      if oneCellType in ReferenceCelltype.keys(): 
         ReferenceCelltype[oneCellType].append(ReferenceCelltype[oneCellType])
      else: ReferenceCelltype[oneCellType] = [oneCellType0]
   DFReferenceProfile = pandas.DataFrame(columns = list(ReferenceCelltype.keys()),
       index = DFReferenceProfile0.index.values)
   for celltype in  DFReferenceProfile.columns.values:
        DFReferenceProfile[celltype] = (  
           DFReferenceProfile0.loc[:, ReferenceCelltype[celltype] ]).mean(axis = 1)
   print("celltype reference matrix:\n", DFReferenceProfile.iloc[0:4, 0:4])
   DFSampleExpressionProfile = pandas.read_table(FileSampleExpressionProfile, sep = "\t", header = 0, index_col = 0)
   print(" initialize a Object For running...") 
   print("environment config(cpus, threads): ", EnvironmentConfig)
   GeneUsedForDeconvolution = SelectGeneForDeconvolution(DFReferenceProfile)
   FileCellTypeCategory = CelltypeCategoryCheck(FileCellTypeCategory, celltypelist = list(ReferenceCelltype.keys()))
   FileInitialCellTypeRatio = InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio, ncelltype = DFReferenceProfile.shape[1]) 
   DFReferenceProfile0 = DFReferenceProfile.loc[GeneUsedForDeconvolution, ]
   DFReferenceProfile0 = DFReferenceProfile0[DFReferenceProfile0.index.isin(DFSampleExpressionProfile.index)]   
   selected_DFSampleExpressionProfile = DFSampleExpressionProfile.loc[DFReferenceProfile0.index]
   selected_DFSampleExpressionProfile = selected_DFSampleExpressionProfile.transpose() 
   SampleList = list(selected_DFSampleExpressionProfile.index) 
   #DFReferenceProfile0 = DFReferenceProfile0.transpose() 
   return CLASS_FOR_RUN(
      DFReferenceProfile0, 
      selected_DFSampleExpressionProfile, 
      SampleList,
      EnvironmentConfig,
      #InitialCellTypeRatio = DictInitialCellTypeRatio)
      InitialCellTypeRatio = InitialCellTypeRatio,
      FileCellTypeCategory = FileCellTypeCategory,
      FileInitialCellTypeRatio = FileInitialCellTypeRatio,) 
