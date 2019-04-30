""" Analyze MCMC output - chain length, etc. """

# Built-in libraries
import glob
import os
import pickle
# External libraries
import cartopy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
import numpy as np
import pandas as pd
#import pymc
#from scipy import stats
#from scipy.stats.kde import gaussian_kde
#from scipy.stats import norm
#from scipy.stats import truncnorm
#from scipy.stats import uniform
#from scipy.stats import linregress
#from scipy.stats import lognorm
#from scipy.optimize import minimize
import xarray as xr
# Local libraries
import class_climate
import class_mbdata
import pygem_input as input
import pygemfxns_gcmbiasadj as gcmbiasadj
import pygemfxns_massbalance as massbalance
import pygemfxns_modelsetup as modelsetup
import run_calibration as calibration

# Script options
option_plot_cmip5_normalizedchange = 0
option_cmip5_heatmap_w_volchange = 0
option_map_gcm_changes = 0
option_region_map_nodata = 0

option_glaciermip_table = 1


#%% ===== Input data =====
netcdf_fp_cmip5 = input.output_sim_fp + 'spc_subset/'
netcdf_fp_era = input.output_sim_fp + '/ERA-Interim/ERA-Interim_1980_2017_nochg'

#%%
regions = [13, 14, 15]

# GCMs and RCP scenarios
gcm_names = ['CanESM2', 'CCSM4', 'CNRM-CM5', 'CSIRO-Mk3-6-0',  'GFDL-CM3', 'GFDL-ESM2M', 'GISS-E2-R', 'IPSL-CM5A-LR', 
             'MPI-ESM-LR', 'NorESM1-M']
#gcm_names = ['CanESM2', 'CCSM4', 'CNRM-CM5', 'CSIRO-Mk3-6-0',  'GFDL-CM3', 'GFDL-ESM2M', 'IPSL-CM5A-LR', 
#             'MPI-ESM-LR', 'NorESM1-M']
#gcm_names = ['CanESM2', 'CCSM4']
#gcm_names = ['GISS-E2-R']
rcps = ['rcp26', 'rcp45', 'rcp85']
#rcps = ['rcp26', 'rcp85']
#rcps = ['rcp85']

# Grouping
#grouping = 'all'
grouping = 'rgi_region'
#grouping = 'watershed'
#grouping = 'kaab'
#grouping = 'degree'

degree_size = 0.5

vn_title_dict = {'massbal':'Mass\nBalance',                                                                      
                 'precfactor':'Precipitation\nFactor',                                                              
                 'tempchange':'Temperature\nBias',                                                               
                 'ddfsnow':'Degree-Day \nFactor of Snow'}
vn_label_dict = {'massbal':'Mass Balance\n[mwea]',                                                                      
                 'precfactor':'Precipitation Factor\n[-]',                                                              
                 'tempchange':'Temperature Bias\n[$^\circ$C]',                                                               
                 'ddfsnow':'Degree Day Factor of Snow\n[mwe d$^{-1}$ $^\circ$C$^{-1}$]',
                 'dif_masschange':'Mass Balance [mwea]\n(Observation - Model)'}
vn_label_units_dict = {'massbal':'[mwea]',                                                                      
                       'precfactor':'[-]',                                                              
                       'tempchange':'[$^\circ$C]',                                                               
                       'ddfsnow':'[mwe d$^{-1}$ $^\circ$C$^{-1}$]'}
title_dict = {'Amu_Darya': 'Amu Darya',
              'Brahmaputra': 'Brahmaputra',
              'Ganges': 'Ganges',
              'Ili': 'Ili',
              'Indus': 'Indus',
              'Inner_Tibetan_Plateau': 'Inner TP',
              'Inner_Tibetan_Plateau_extended': 'Inner TP ext',
              'Irrawaddy': 'Irrawaddy',
              'Mekong': 'Mekong',
              'Salween': 'Salween',
              'Syr_Darya': 'Syr Darya',
              'Tarim': 'Tarim',
              'Yangtze': 'Yangtze',
              'inner_TP': 'Inner TP',
              'Karakoram': 'Karakoram',
              'Yigong': 'Yigong',
              'Yellow': 'Yellow',
              'Bhutan': 'Bhutan',
              'Everest': 'Everest',
              'West Nepal': 'West Nepal',
              'Spiti Lahaul': 'Spiti Lahaul',
              'tien_shan': 'Tien Shan',
              'Pamir': 'Pamir',
              'pamir_alai': 'Pamir Alai',
              'Kunlun': 'Kunlun',
              'Hindu Kush': 'Hindu Kush',
              13: 'Central Asia',
              14: 'South Asia West',
              15: 'South Asia East',
              'all': 'HMA'
              }
title_location = {'Syr_Darya': [68, 46.1],
                  'Ili': [83.6, 45.5],
                  'Amu_Darya': [64.6, 36.9],
                  'Tarim': [83.0, 39.2],
                  'Inner_Tibetan_Plateau_extended': [100, 40],
                  'Indus': [70.7, 31.9],
                  'Inner_Tibetan_Plateau': [85, 32.4],
                  'Yangtze': [106.0, 29.8],
                  'Ganges': [81.3, 26.6],
                  'Brahmaputra': [92.0, 26],
                  'Irrawaddy': [96.2, 23.8],
                  'Salween': [98.5, 20.8],
                  'Mekong': [103.8, 17.5],
                  'Yellow': [106.0, 36],
                  13: [84,39],
                  14: [72, 33],
                  15: [84,26.8],
                  'inner_TP': [89, 33.5],
                  'Karakoram': [68.7, 33],
                  'Yigong': [97.5, 26.2],
                  'Bhutan': [92.1, 26],
                  'Everest': [85, 26.3],
                  'West Nepal': [76.5, 28],
                  'Spiti Lahaul': [70, 31.4],
                  'tien_shan': [80, 42],
                  'Pamir': [66, 36],
                  'pamir_alai': [65.2, 40.2],
                  'Kunlun': [79, 37.5],
                  'Hindu Kush': [64, 34.5]
                  }
vn_dict = {'volume_glac_annual': 'Volume [-]',
           'volume_norm': 'Normalized Volume Remaining [-]',
           'runoff_glac_annual': 'Normalized Runoff [-]',
           'runoff_glac_monthly': 'Normalized Runoff [-]',
           'peakwater': 'Peak Water [yr]',
           'temp_glac_annual': 'Temperature [$^\circ$C]',
           'prec_glac_annual': 'Precipitation [m]',
           'precfactor': 'Precipitation Factor [-]',
           'tempchange': 'Temperature bias [$^\circ$C]', 
           'ddfsnow': 'DDFsnow [mm w.e. d$^{-1}$ $^\circ$C$^{-1}$]'}
rcp_dict = {'rcp26': '2.6',
            'rcp45': '4.5',
            'rcp60': '6.0',
            'rcp85': '8.5'}
# Colors list
colors_rgb = [(0.00, 0.57, 0.57), (0.71, 0.43, 1.00), (0.86, 0.82, 0.00), (0.00, 0.29, 0.29), (0.00, 0.43, 0.86), 
              (0.57, 0.29, 0.00), (1.00, 0.43, 0.71), (0.43, 0.71, 1.00), (0.14, 1.00, 0.14), (1.00, 0.71, 0.47), 
              (0.29, 0.00, 0.57), (0.57, 0.00, 0.00), (0.71, 0.47, 1.00), (1.00, 1.00, 0.47)]
gcm_colordict = dict(zip(gcm_names, colors_rgb[0:len(gcm_names)]))
rcp_colordict = {'rcp26':'b', 'rcp45':'k', 'rcp60':'m', 'rcp85':'r'}
rcp_styledict = {'rcp26':':', 'rcp45':'--', 'rcp85':'-.'}

cal_datasets = ['shean']

# Bounds (90% bounds --> 95% above/below given threshold)
low_percentile = 5
high_percentile = 95

colors = ['#387ea0', '#fcb200', '#d20048']
linestyles = ['-', '--', ':']

# Group dictionaries
watershed_dict_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/rgi60_HMA_dict_watershed.csv'
watershed_csv = pd.read_csv(watershed_dict_fn)
watershed_dict = dict(zip(watershed_csv.RGIId, watershed_csv.watershed))
kaab_dict_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/rgi60_HMA_dict_kaab.csv'
kaab_csv = pd.read_csv(kaab_dict_fn)
kaab_dict = dict(zip(kaab_csv.RGIId, kaab_csv.kaab_name))

# Shapefiles
rgiO1_shp_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/RGI/rgi60/00_rgi60_regions/00_rgi60_O1Regions.shp'
rgi_glac_shp_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/rgi60_HMA.shp'
watershed_shp_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/HMA_basins_20181018_4plot.shp'
kaab_shp_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/kaab2015_regions.shp'
srtm_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/SRTM_HMA.tif'
srtm_contour_fn = '/Users/davidrounce/Documents/Dave_Rounce/HiMAT/qgis_himat/SRTM_HMA_countours_2km_gt3000m_smooth.shp'

# GRACE mascons
mascon_fp = input.main_directory + '/../GRACE/GSFC.glb.200301_201607_v02.4/'
mascon_fn = 'mascon.txt'
mascon_cns = ['CenLat', 'CenLon', 'LatWidth', 'LonWidth', 'Area_arcdeg', 'Area_km2', 'location', 'basin', 
              'elevation_flag']
mascon_df = pd.read_csv(mascon_fp + mascon_fn, header=None, names=mascon_cns, skiprows=14, 
                        delim_whitespace=True)
mascon_df = mascon_df.sort_values(by=['CenLat', 'CenLon'])
mascon_df.reset_index(drop=True, inplace=True)

east = 104
west = 67
south = 25
north = 48


#%% ===== FUNCTIONS =====
def select_groups(grouping, main_glac_rgi_all):
    """
    Select groups based on grouping
    """
    if grouping == 'rgi_region':
        groups = main_glac_rgi_all.O1Region.unique().tolist()
        group_cn = 'O1Region'
    elif grouping == 'watershed':
        groups = main_glac_rgi_all.watershed.unique().tolist()
        group_cn = 'watershed'
    elif grouping == 'kaab':
        groups = main_glac_rgi_all.kaab.unique().tolist()
        group_cn = 'kaab'
        groups = [x for x in groups if str(x) != 'nan']  
    elif grouping == 'degree':
        groups = main_glac_rgi_all.deg_id.unique().tolist()
        group_cn = 'deg_id'
    elif grouping == 'mascon':
        groups = main_glac_rgi_all.mascon_idx.unique().tolist()
        groups = [int(x) for x in groups]
        group_cn = 'mascon_idx'
    else:
        groups = ['all']
        group_cn = 'all_group'
    try:
        groups = sorted(groups, key=str.lower)
    except:
        groups = sorted(groups)
    return groups, group_cn


def load_glacier_data(rgi_regions):
    """
    Load glacier data (main_glac_rgi, hyps, and ice thickness)
    """
    for rgi_region in rgi_regions:
        # Data on all glaciers
        main_glac_rgi_region = modelsetup.selectglaciersrgitable(rgi_regionsO1=[rgi_region], rgi_regionsO2 = 'all', 
                                                                 rgi_glac_number='all')
         # Glacier hypsometry [km**2]
        main_glac_hyps_region = modelsetup.import_Husstable(main_glac_rgi_region, [rgi_region], input.hyps_filepath,
                                                            input.hyps_filedict, input.hyps_colsdrop)
        # Ice thickness [m], average
        main_glac_icethickness_region= modelsetup.import_Husstable(main_glac_rgi_region, [rgi_region], 
                                                                 input.thickness_filepath, input.thickness_filedict, 
                                                                 input.thickness_colsdrop)
        if rgi_region == rgi_regions[0]:
            main_glac_rgi_all = main_glac_rgi_region
            main_glac_hyps_all = main_glac_hyps_region
            main_glac_icethickness_all = main_glac_icethickness_region
        else:
            main_glac_rgi_all = pd.concat([main_glac_rgi_all, main_glac_rgi_region], sort=False)
            main_glac_hyps_all = pd.concat([main_glac_hyps_all, main_glac_hyps_region], sort=False)
            main_glac_icethickness_all = pd.concat([main_glac_icethickness_all, main_glac_icethickness_region], 
                                                   sort=False)
    main_glac_hyps_all = main_glac_hyps_all.fillna(0)
    main_glac_icethickness_all = main_glac_icethickness_all.fillna(0)
    
    # Add watersheds, regions, degrees, mascons, and all groups to main_glac_rgi_all
    # Watersheds
    main_glac_rgi_all['watershed'] = main_glac_rgi_all.RGIId.map(watershed_dict)
    # Regions
    main_glac_rgi_all['kaab'] = main_glac_rgi_all.RGIId.map(kaab_dict)
    # Degrees
    main_glac_rgi_all['CenLon_round'] = np.floor(main_glac_rgi_all.CenLon.values/degree_size) * degree_size
    main_glac_rgi_all['CenLat_round'] = np.floor(main_glac_rgi_all.CenLat.values/degree_size) * degree_size
    deg_groups = main_glac_rgi_all.groupby(['CenLon_round', 'CenLat_round']).size().index.values.tolist()
    deg_dict = dict(zip(deg_groups, np.arange(0,len(deg_groups))))
    main_glac_rgi_all.reset_index(drop=True, inplace=True)
    cenlon_cenlat = [(main_glac_rgi_all.loc[x,'CenLon_round'], main_glac_rgi_all.loc[x,'CenLat_round']) 
                     for x in range(len(main_glac_rgi_all))]
    main_glac_rgi_all['CenLon_CenLat'] = cenlon_cenlat
    main_glac_rgi_all['deg_id'] = main_glac_rgi_all.CenLon_CenLat.map(deg_dict)
#    # Mascons
#    if grouping == 'mascon':
#        main_glac_rgi_all['mascon_idx'] = np.nan
#        for glac in range(main_glac_rgi_all.shape[0]):
#            latlon_dist = (((mascon_df.CenLat.values - main_glac_rgi_all.CenLat.values[glac])**2 + 
#                             (mascon_df.CenLon.values - main_glac_rgi_all.CenLon.values[glac])**2)**0.5)
#            main_glac_rgi_all.loc[glac,'mascon_idx'] = [x[0] for x in np.where(latlon_dist == latlon_dist.min())][0]
#        mascon_groups = main_glac_rgi_all.mascon_idx.unique().tolist()
#        mascon_groups = [int(x) for x in mascon_groups]
#        mascon_groups = sorted(mascon_groups)
#        mascon_latlondict = dict(zip(mascon_groups, mascon_df[['CenLat', 'CenLon']].values[mascon_groups].tolist()))
    # All
    main_glac_rgi_all['all_group'] = 'all'
    
    return main_glac_rgi_all, main_glac_hyps_all, main_glac_icethickness_all


def retrieve_gcm_data(gcm_name, rcp, main_glac_rgi, option_bias_adjustment=input.option_bias_adjustment):
    """ Load temperature, precipitation, and elevation data associated with GCM/RCP
    """
    regions = list(set(main_glac_rgi.O1Region.tolist()))
    for region in regions:
        main_glac_rgi_region = main_glac_rgi.loc[main_glac_rgi['O1Region'] == region]
        main_glac_rgi_region.reset_index(drop=True, inplace=True)
        
        gcm = class_climate.GCM(name=gcm_name, rcp_scenario=rcp)
    
        # Air temperature [degC], Precipitation [m], Elevation [m asl]
        gcm_temp, gcm_dates = gcm.importGCMvarnearestneighbor_xarray(gcm.temp_fn, gcm.temp_vn, main_glac_rgi_region, 
                                                                     dates_table)
        # 
        gcm_prec, gcm_dates = gcm.importGCMvarnearestneighbor_xarray(gcm.prec_fn, gcm.prec_vn, main_glac_rgi_region, 
                                                                     dates_table)
        # Elevation [m asl]
        gcm_elev = gcm.importGCMfxnearestneighbor_xarray(gcm.elev_fn, gcm.elev_vn, main_glac_rgi_region)          

        # Adjust reference dates in event that reference is longer than GCM data
        if input.startyear >= input.gcm_startyear:
            ref_startyear = input.startyear
        else:
            ref_startyear = input.gcm_startyear
        if input.endyear <= input.gcm_endyear:
            ref_endyear = input.endyear
        else:
            ref_endyear = input.gcm_endyear
        dates_table_ref = modelsetup.datesmodelrun(startyear=ref_startyear, endyear=ref_endyear, 
                                                   spinupyears=input.spinupyears, 
                                                   option_wateryear=input.option_wateryear)
        # Monthly average from reference climate data
        ref_gcm = class_climate.GCM(name=input.ref_gcm_name)
           
        # ===== BIAS CORRECTIONS =====
        # No adjustments
        if option_bias_adjustment == 0:
            gcm_temp_adj = gcm_temp
            gcm_prec_adj = gcm_prec
            gcm_elev_adj = gcm_elev
        # Bias correct based on reference climate data
        else:
            # Air temperature [degC], Precipitation [m], Elevation [masl], Lapse rate [K m-1]
            ref_temp, ref_dates = ref_gcm.importGCMvarnearestneighbor_xarray(ref_gcm.temp_fn, ref_gcm.temp_vn, 
                                                                             main_glac_rgi_region, dates_table_ref)
            ref_prec, ref_dates = ref_gcm.importGCMvarnearestneighbor_xarray(ref_gcm.prec_fn, ref_gcm.prec_vn, 
                                                                             main_glac_rgi_region, dates_table_ref)
            ref_elev = ref_gcm.importGCMfxnearestneighbor_xarray(ref_gcm.elev_fn, ref_gcm.elev_vn, 
                                                                 main_glac_rgi_region)
            
            # OPTION 1: Adjust temp using Huss and Hock (2015), prec similar but addresses for variance and outliers
            if input.option_bias_adjustment == 1:
                # Temperature bias correction
                gcm_temp_adj, gcm_elev_adj = gcmbiasadj.temp_biasadj_HH2015(ref_temp, ref_elev, gcm_temp, 
                                                                            dates_table_ref, dates_table)
                # Precipitation bias correction
                gcm_prec_adj, gcm_elev_adj = gcmbiasadj.prec_biasadj_opt1(ref_prec, ref_elev, gcm_prec, 
                                                                          dates_table_ref, dates_table)
            
            # OPTION 2: Adjust temp and prec using Huss and Hock (2015)
            elif input.option_bias_adjustment == 2:
                # Temperature bias correction
                gcm_temp_adj, gcm_elev_adj = gcmbiasadj.temp_biasadj_HH2015(ref_temp, ref_elev, gcm_temp, 
                                                                            dates_table_ref, dates_table)
                # Precipitation bias correction
                gcm_prec_adj, gcm_elev_adj = gcmbiasadj.prec_biasadj_HH2015(ref_prec, ref_elev, gcm_prec, 
                                                                            dates_table_ref, dates_table)
        # Concatenate datasets
        if region == regions[0]:
            gcm_temp_adj_all = gcm_temp_adj
            gcm_prec_adj_all = gcm_prec_adj
            gcm_elev_adj_all = gcm_elev_adj
        else:
            gcm_temp_adj_all = np.vstack([gcm_temp_adj_all, gcm_temp_adj])
            gcm_prec_adj_all = np.vstack([gcm_prec_adj_all, gcm_prec_adj])
            gcm_elev_adj_all = np.concatenate([gcm_elev_adj_all, gcm_elev_adj])
    
    return gcm_temp_adj_all, gcm_prec_adj_all, gcm_elev_adj_all
    


#%%
if option_cmip5_heatmap_w_volchange == 1:
    vns_heatmap = ['massbaltotal_glac_monthly', 'temp_glac_monthly', 'prec_glac_monthly']
    figure_fp = input.output_sim_fp + 'figures/'
    
    option_plot_multimodel = 1
    option_plot_single = 0

    area_cutoffs = [1]
    nyears = 18

    multimodel_linewidth = 2
    alpha=0.2
    
    # Load glaciers
    main_glac_rgi, main_glac_hyps, main_glac_icethickness = load_glacier_data(regions)
    
    # Groups
    groups, group_cn = select_groups(grouping, main_glac_rgi)
    
    # Select dates including future projections
    dates_table = modelsetup.datesmodelrun(startyear=input.gcm_startyear, endyear=input.gcm_endyear, 
                                           spinupyears=input.gcm_spinupyears, option_wateryear=input.gcm_wateryear)
    
    # Glacier and grouped annual specific mass balance and mass change
    for rcp in rcps:
        for ngcm, gcm_name in enumerate(gcm_names):
            
            print(rcp, gcm_name)
            
            # Climate data
            temp_glac_all, prectotal_glac_all, elev_glac_all = retrieve_gcm_data(gcm_name, rcp, main_glac_rgi)
            
            # Extract data from netcdf
            group_glacidx = {}
            vol_group_dict = {}
            temp_group_dict = {}
            prectotal_group_dict = {}
            
            for region in regions:
                       
                # Load datasets
                ds_fn = ('R' + str(region) + '_' + gcm_name + '_' + rcp + '_c2_ba' + str(input.option_bias_adjustment) +
                         '_100sets_2000_2100--subset.nc')
                ds = xr.open_dataset(netcdf_fp_cmip5 + ds_fn)
                # Extract time variable
                time_values_annual = ds.coords['year_plus1'].values
                time_values_monthly = ds.coords['time'].values
                
                # Merge datasets
                if region == regions[0]:
                    # Volume
                    vol_glac_all = ds['volume_glac_annual'].values[:,:,0]
                    vol_glac_std_all = ds['volume_glac_annual'].values[:,:,1]
                    # Area
                    area_glac_all = ds['area_glac_annual'].values[:,:,0]
                    area_glac_std_all = ds['area_glac_annual'].values[:,:,1]
                    # Mass balance
                    mb_glac_all = ds['massbaltotal_glac_monthly'].values[:,:,0]
                    mb_glac_std_all = ds['massbaltotal_glac_monthly'].values[:,:,1]
                else:
                    # Volume
                    vol_glac_all = np.concatenate((vol_glac_all, ds['volume_glac_annual'].values[:,:,0]), axis=0)
                    vol_glac_std_all = np.concatenate((vol_glac_std_all, ds['volume_glac_annual'].values[:,:,1]),axis=0)
                    # Area
                    area_glac_all = np.concatenate((area_glac_all, ds['area_glac_annual'].values[:,:,0]), axis=0)
                    area_glac_std_all = np.concatenate((area_glac_std_all, ds['area_glac_annual'].values[:,:,1]),axis=0)
                    # Mass balance
                    mb_glac_all = np.concatenate((mb_glac_all, ds['massbaltotal_glac_monthly'].values[:,:,0]), axis=0)
                    mb_glac_std_all = np.concatenate((mb_glac_std_all, ds['massbaltotal_glac_monthly'].values[:,:,1]),axis=0)
    
                ds.close()
               
            # Annual Mass Balance
            mb_glac_all_annual = gcmbiasadj.annual_sum_2darray(mb_glac_all)
            # mask values where volume is zero
            mb_glac_all_annual[vol_glac_all[:,:-1] == 0] = np.nan
            
            # Annual Temperature, Precipitation, and Accumulation
            temp_glac_all_annual = gcmbiasadj.annual_avg_2darray(temp_glac_all)
            prectotal_glac_all_annual = gcmbiasadj.annual_sum_2darray(prectotal_glac_all)
            
            # Groups
            for ngroup, group in enumerate(groups):
                # Select subset of data
                group_glac_indices = main_glac_rgi.loc[main_glac_rgi[group_cn] == group].index.values.tolist()
                group_glacidx[group] = group_glac_indices
                
                # Regional Volume, and Area-weighted Temperature and Precipitation
                vol_group_all = vol_glac_all[group_glac_indices,:].sum(axis=0)
                
                temp_group_all = ((temp_glac_all_annual[group_glac_indices,:] * 
                                   area_glac_all[group_glac_indices,:][:,0][:,np.newaxis]).sum(axis=0) / 
                                  area_glac_all[group_glac_indices,:][:,0].sum())
                prectotal_group_all = ((prectotal_glac_all_annual[group_glac_indices,:] * 
                                        area_glac_all[group_glac_indices,:][:,0][:,np.newaxis]).sum(axis=0) / 
                                       area_glac_all[group_glac_indices,:][:,0].sum())
                    
                # Expand dimensions for multi-model calculations
                vol_group_all = np.expand_dims(vol_group_all, axis=1)
                temp_group_all = np.expand_dims(temp_group_all, axis=1)
                prectotal_group_all = np.expand_dims(prectotal_group_all, axis=1)

                vol_group_dict[group] = vol_group_all
                temp_group_dict[group] = temp_group_all
                prectotal_group_dict[group] = prectotal_group_all
                
            # Expand dimensions for multi-model calculations
            mb_glac_all_annual = np.expand_dims(mb_glac_all_annual, axis=2)
            temp_glac_all_annual = np.expand_dims(temp_glac_all_annual, axis=2)
            prectotal_glac_all_annual = np.expand_dims(prectotal_glac_all_annual, axis=2)
            
            # ===== MULTI-MODEL =====
            if ngcm == 0:
                mb_glac_all_annual_multimodel = mb_glac_all_annual
                temp_glac_all_annual_multimodel = temp_glac_all_annual
                prectotal_glac_all_annual_multimodel = prectotal_glac_all_annual
                
                vol_group_dict_multimodel = vol_group_dict
                temp_group_dict_multimodel = temp_group_dict
                prectotal_group_dict_multimodel = prectotal_group_dict
                
            else:
                mb_glac_all_annual_multimodel = np.append(mb_glac_all_annual_multimodel, 
                                                          mb_glac_all_annual, axis=2)
                temp_glac_all_annual_multimodel = np.append(temp_glac_all_annual_multimodel, 
                                                            temp_glac_all_annual, axis=2)
                prectotal_glac_all_annual_multimodel = np.append(prectotal_glac_all_annual_multimodel, 
                                                                 prectotal_glac_all_annual, axis=2)
                
                for ngroup, group in enumerate(groups):
                    vol_group_dict_multimodel[group] = np.append(vol_group_dict_multimodel[group], 
                                                                 vol_group_dict[group], axis=1)
                    temp_group_dict_multimodel[group] = np.append(temp_group_dict_multimodel[group], 
                                                                  temp_group_dict[group], axis=1)
                    prectotal_group_dict_multimodel[group] = np.append(prectotal_group_dict_multimodel[group], 
                                                                       prectotal_group_dict[group], axis=1)


#%%        
        def plot_heatmap(rcp, mb_glac_all_annual, temp_glac_all_annual, prectotal_glac_all_annual, 
                         vol_group_dict, temp_group_dict, prectotal_group_dict, gcm_name=None):
            cmap_dict = {'massbaltotal_glac_monthly':'RdYlBu',
                         'temp_glac_monthly':'RdYlBu_r',
                         'prec_glac_monthly':'RdYlBu'}
            norm_dict = {'massbaltotal_glac_monthly':plt.Normalize(-2,2),
                         'temp_glac_monthly':plt.Normalize(0,6),
                         'prec_glac_monthly':plt.Normalize(0.9,1.15)}
#            ylabel_dict = {'massbaltotal_glac_monthly':'Normalized Volume\n[-]',
#                           'temp_glac_monthly':'Temperature Change\n[$^\circ$C]',
#                           'prec_glac_monthly':'Precipitation Change\n[%]'}
            line_label_dict = {'massbaltotal_glac_monthly':'Regional volume [-]',
                               'temp_glac_monthly':'Regional mean',
                               'prec_glac_monthly':'Regional mean'}
            line_loc_dict = {'massbaltotal_glac_monthly':(0.17,0.85),
                             'temp_glac_monthly':(0.47,0.85),
                             'prec_glac_monthly':(0.75,0.85)}
#            colorbar_dict = {'massbaltotal_glac_monthly':(0.23, 1.02, 'Mass Balance\n[mwea]', 
#                                                          [0.125, 0.92, 0.215, 0.02]),
#                             'temp_glac_monthly':(0.51, 1.02, 'Temperature Change\n[$^\circ$C]',
#                                                 [0.125, 0.92, 0.215, 0.02]),
#                             'prec_glac_monthly':(0.79, 1.02, 'Precipitation Change\n[%]',
#                                                 [0.405, 0.92, 0.215, 0.02])
#                             }
            
            
            for area_cutoff in area_cutoffs:
                
                # Plot the normalized volume change for each region, along with the mass balances
                fig, ax = plt.subplots(len(groups), len(vns_heatmap), squeeze=False, sharex=True, sharey=False, 
                                       gridspec_kw = {'wspace':0.3, 'hspace':0.1})
                fig.subplots_adjust(top=0.88)
            
                
                for nvar, vn_heatmap in enumerate(vns_heatmap):
                    
                    cmap = cmap_dict[vn_heatmap]
                    norm = norm_dict[vn_heatmap]
                    
                    for nregion, region in enumerate(regions):

                        if vn_heatmap == 'massbaltotal_glac_monthly':
                            zmesh = mb_glac_all_annual
                            var_line = vol_group_dict[region][:-1] / vol_group_dict[region][0]
                            
                        elif vn_heatmap == 'temp_glac_monthly':
                            zmesh = temp_glac_all_annual - temp_glac_all_annual[:,0:nyears].mean(axis=1)[:,np.newaxis]
                            var_line = temp_group_dict[region] - temp_group_dict[region][0:nyears].mean()
                            
                        elif vn_heatmap == 'prec_glac_monthly':
                            zmesh = (prectotal_glac_all_annual /
                                     prectotal_glac_all_annual[:,0:nyears].mean(axis=1)[:,np.newaxis])
                            var_line = prectotal_group_dict[region] / prectotal_group_dict[region][0:nyears].mean()
                            
                        # HEATMAP (only glaciers greater than area threshold)
                        glac_idx4mesh = np.where(main_glac_rgi.loc[group_glacidx[region],'Area'] > area_cutoff)[0]
                        z = zmesh[glac_idx4mesh,:]
                        x = time_values_annual[:-1]
                        y = np.array(range(len(glac_idx4mesh)))
                        ax[nregion,nvar].pcolormesh(x, y, z, cmap=cmap, norm=norm)
                        if nvar > 0:
                            ax[nregion,nvar].yaxis.set_ticklabels([])
                             
                        # LINE
                        ax2 = ax[nregion,nvar].twinx()
                        ax2.plot(time_values_annual[:-1], var_line, color='gray', linewidth=1, label=str(region))
                        ax2.tick_params(axis='y', colors='gray')
                        ax2.set_zorder(2)
                        ax2.patch.set_visible(False)
                        ax2.set_xlim([time_values_annual[0], time_values_annual[-2]])
                        if vn_heatmap == 'massbaltotal_glac_monthly':
                            ax2.set_ylim([0,1.05])
                            ax2.yaxis.set_ticks(np.arange(0,1.05,0.2))
                        elif vn_heatmap == 'temp_glac_monthly' and gcm_name == None and rcp == 'rcp85':
                            ax2.set_ylim([-0.5, 6.1])
                            ax2.yaxis.set_ticks(np.arange(0,6.1,2))
                        elif vn_heatmap == 'prec_glac_monthly' and gcm_name == None and rcp == 'rcp85':
                            ax2.set_ylim([0.9, 1.15])
                            ax2.yaxis.set_ticks(np.arange(0.9,1.21,0.1))
                            

                    # Line legend
                    line = Line2D([0,1],[0,1], linestyle='-', color='gray')
                    leg_line = [line]
                    leg_label = [line_label_dict[vn_heatmap]]
                    leg = fig.legend(leg_line, leg_label, loc='upper left', 
                                     bbox_to_anchor=line_loc_dict[vn_heatmap], 
                                     handlelength=1.5, handletextpad=0.5, borderpad=0, frameon=False)
                    for text in leg.get_texts():
                        text.set_color('gray')
                    

    #                # COLORBARS
    #                fig.text(colorbar_dict[vn_heatmap][0], colorbar_dict[vn_heatmap][1], colorbar_dict[vn_heatmap][2], 
    #                         ha='center', va='center', size=12)
    #                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    #                sm._A = []
    #                cax = plt.axes(colorbar_dict[vn_heatmap][3])
    #                plt.colorbar(sm, cax=cax, orientation='horizontal')
    #                cax.xaxis.set_ticks_position('top')
    #                for n, label in enumerate(cax.xaxis.get_ticklabels()):
    #                    if n%2 != 0:
    #                        label.set_visible(False)
                
                # Mass balance colorbar
                fig.text(0.23, 1.02, 'Mass Balance\n[mwea]', ha='center', va='center', size=12)
                cmap=cmap_dict['massbaltotal_glac_monthly']
                norm=norm_dict['massbaltotal_glac_monthly']
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm._A = []
                cax = plt.axes([0.125, 0.92, 0.215, 0.02])
                plt.colorbar(sm, cax=cax, orientation='horizontal')
                cax.xaxis.set_ticks_position('top')
                for n, label in enumerate(cax.xaxis.get_ticklabels()):
                    if n%2 != 0:
                        label.set_visible(False)
                
                # Temperature colorbar
                fig.text(0.51, 1.02, 'Temperature Change\n[$^\circ$C]', ha='center', va='center', size=12)
                cmap=cmap_dict['temp_glac_monthly']
                norm=norm_dict['temp_glac_monthly']
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm._A = []
                cax = plt.axes([0.405, 0.92, 0.215, 0.02])
                plt.colorbar(sm, cax=cax, orientation='horizontal')
                cax.xaxis.set_ticks_position('top')
                for n, label in enumerate(cax.xaxis.get_ticklabels()):
                    if n%2 != 0:
                        label.set_visible(False)
                
                # Precipitation colorbar
                fig.text(0.79, 1.02, 'Precipitation Change\n[%]', ha='center', va='center', size=12)
                cmap=cmap_dict['prec_glac_monthly']
                norm=norm_dict['prec_glac_monthly']
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm._A = []
                cax = plt.axes([0.685, 0.92, 0.215, 0.02])
                plt.colorbar(sm, cax=cax, orientation='horizontal')
                cax.xaxis.set_ticks_position('top')
                for n, label in enumerate(cax.xaxis.get_ticklabels()):
                    if n%2 != 0:
                        label.set_visible(False)
                            
                # Label y-axis
                fig.text(0.035, 0.78, 'Region 13', va='center', rotation='vertical', size=12) 
                fig.text(0.035, 0.51, 'Region 14', va='center', rotation='vertical', size=12) 
                fig.text(0.035, 0.25, 'Region 15', va='center', rotation='vertical', size=12)
                fig.text(-0.01, 0.5, 'Glacier Number \n(only glaciers greater than ' + str(area_cutoff) + 'km$^2$)', 
                         va='center', ha='center', rotation='vertical', size=12)  
                    
                # Save figure
                fig.set_size_inches(8,6)
                if gcm_name == None:
                    figure_fn = ('multimodel_' + rcp + '_' + str(len(gcm_names)) + 'gcms_areagt' + str(area_cutoff) 
                                 + 'km2.png')
                else:
                    figure_fn = gcm_name + '_' + rcp + '_areagt' + str(area_cutoff) + 'km2.png'
                fig.savefig(figure_fp + figure_fn, bbox_inches='tight', dpi=300)
                plt.show()
                plt.close()
                

        if option_plot_multimodel == 1:
            mb_glac_all_annual = mb_glac_all_annual_multimodel.mean(axis=2)
            temp_glac_all_annual = temp_glac_all_annual_multimodel.mean(axis=2)
            prectotal_glac_all_annual = prectotal_glac_all_annual_multimodel.mean(axis=2)
            
            vol_group_dict_single = {}
            temp_group_dict_single = {}
            prectotal_group_dict_single = {}
            for ngroup, group in enumerate(groups):
                vol_group_dict_single[group] = vol_group_dict_multimodel[group].mean(axis=1)
                temp_group_dict_single[group] = temp_group_dict_multimodel[group].mean(axis=1)
                prectotal_group_dict_single[group] = prectotal_group_dict_multimodel[group].mean(axis=1)
                
            plot_heatmap(rcp, mb_glac_all_annual, temp_glac_all_annual, prectotal_glac_all_annual, 
                         vol_group_dict_single, temp_group_dict_single, prectotal_group_dict_single)
            
        if option_plot_single == 1:
            for ngcm, gcm_name in enumerate(gcm_names):
                mb_glac_all_annual = mb_glac_all_annual_multimodel[:,:,ngcm]
                temp_glac_all_annual = temp_glac_all_annual_multimodel[:,:,ngcm]
                prectotal_glac_all_annual = prectotal_glac_all_annual_multimodel[:,:,ngcm]
                
                vol_group_dict_single = {}
                temp_group_dict_single = {}
                prectotal_group_dict_single = {}
                for ngroup, group in enumerate(groups):
                    vol_group_dict_single[group] = vol_group_dict_multimodel[group][:,ngcm]
                    temp_group_dict_single[group] = temp_group_dict_multimodel[group][:,ngcm]
                    prectotal_group_dict_single[group] = prectotal_group_dict_multimodel[group][:,ngcm]
                    
                plot_heatmap(rcp, mb_glac_all_annual, temp_glac_all_annual, prectotal_glac_all_annual, 
                             vol_group_dict_single, temp_group_dict_single, prectotal_group_dict_single,
                             gcm_name=gcm_name)
        
#%%
if option_map_gcm_changes == 1:
    figure_fp = input.output_sim_fp + 'figures/gcm_changes/'
    if os.path.exists(figure_fp) == False:
        os.makedirs(figure_fp)
            
    nyears = 30
    
    temp_vn = 'tas'
    prec_vn = 'pr'
    elev_vn = 'orog'
    lat_vn = 'lat'
    lon_vn = 'lon'
    time_vn = 'time'
    
    xtick = 5
    ytick = 5
    xlabel = 'Longitude [$^\circ$]'
    ylabel = 'Latitude [$^\circ$]'
    labelsize = 12
    
#    # Extra information
#    self.timestep = input.timestep
#    self.rgi_lat_colname=input.rgi_lat_colname
#    self.rgi_lon_colname=input.rgi_lon_colname
#    self.rcp_scenario = rcp_scenario
    
    # Select dates including future projections
    dates_table = modelsetup.datesmodelrun(startyear=2000, endyear=2100, spinupyears=1, option_wateryear=1)
    
    for rcp in rcps:
        for ngcm, gcm_name in enumerate(gcm_names):
            
            # Variable filepaths
            var_fp = input.cmip5_fp_var_prefix + rcp + input.cmip5_fp_var_ending
            fx_fp = input.cmip5_fp_fx_prefix + rcp + input.cmip5_fp_fx_ending
            # Variable filenames
            temp_fn = temp_vn + '_mon_' + gcm_name + '_' + rcp + '_r1i1p1_native.nc'
            prec_fn = prec_vn + '_mon_' + gcm_name + '_' + rcp + '_r1i1p1_native.nc'
            elev_fn = elev_vn + '_fx_' + gcm_name + '_' + rcp+ '_r0i0p0.nc'
            
            # Import netcdf file
            ds_temp = xr.open_dataset(var_fp + temp_fn)
            ds_prec = xr.open_dataset(var_fp + prec_fn)
            
            # Time, Latitude, Longitude
            start_idx = (np.where(pd.Series(ds_temp[time_vn])
                                  .apply(lambda x: x.strftime('%Y-%m')) == dates_table['date']
                                  .apply(lambda x: x.strftime('%Y-%m'))[0]))[0][0]
            end_idx = (np.where(pd.Series(ds_temp[time_vn])
                                .apply(lambda x: x.strftime('%Y-%m')) == dates_table['date']
                                .apply(lambda x: x.strftime('%Y-%m'))[dates_table.shape[0] - 1]))[0][0]
            north_idx = np.abs(north - ds_temp[lat_vn][:].values).argmin()
            south_idx = np.abs(south - ds_temp[lat_vn][:].values).argmin()
            west_idx = np.abs(west - ds_temp[lon_vn][:].values).argmin()
            east_idx = np.abs(east - ds_temp[lon_vn][:].values).argmin()
            
            lats = ds_temp[lat_vn][south_idx:north_idx+1].values
            lons = ds_temp[lon_vn][west_idx:east_idx+1].values
            temp = ds_temp[temp_vn][start_idx:end_idx+1, south_idx:north_idx+1, west_idx:east_idx+1].values - 273.15
            prec = ds_prec[prec_vn][start_idx:end_idx+1, south_idx:north_idx+1, west_idx:east_idx+1].values
            # Convert from kg m-2 s-1 to m day-1
            prec = prec/1000*3600*24
            
            temp_end = temp[-nyears*12:,:,:].mean(axis=0)
            temp_start = temp[:nyears*12,:,:].mean(axis=0)
            temp_change = temp_end - temp_start
            
            prec_end = prec[-nyears*12:,:,:].mean(axis=0)*365
            prec_start = prec[:nyears*12:,:,:].mean(axis=0)*365
            prec_change = prec_end / prec_start
            
            for vn in ['temp', 'prec']:
#            for vn in ['prec']:
                if vn == 'temp':
                    var_change = temp_change
                    cmap = 'RdYlBu_r'
                    norm = plt.Normalize(int(temp_change.min()), np.ceil(temp_change.max()))
                    var_label = 'Temperature Change [$^\circ$C]'
                elif vn == 'prec':
                    var_change = prec_change
                    cmap = 'RdYlBu'
                    norm = plt.Normalize(0.5, 1.5)
                    var_label = 'Precipitation Change [-]'
                    
                # Create the projection
                fig, ax = plt.subplots(1, 1, figsize=(10,5), subplot_kw={'projection':cartopy.crs.PlateCarree()})
                # Add country borders for reference
                ax.add_feature(cartopy.feature.BORDERS, alpha=0.15, zorder=10)
                ax.add_feature(cartopy.feature.COASTLINE)
    
                # Set the extent
                ax.set_extent([east, west, south, north], cartopy.crs.PlateCarree())    
                # Label title, x, and y axes
                ax.set_xticks(np.arange(east,west+1,xtick), cartopy.crs.PlateCarree())
                ax.set_yticks(np.arange(south,north+1,ytick), cartopy.crs.PlateCarree())
                ax.set_xlabel(xlabel, size=labelsize)
                ax.set_ylabel(ylabel, size=labelsize)
                
                # Add contour lines
                srtm_contour_shp = cartopy.io.shapereader.Reader(srtm_contour_fn)
                srtm_contour_feature = cartopy.feature.ShapelyFeature(srtm_contour_shp.geometries(), cartopy.crs.PlateCarree(),
                                                                      edgecolor='black', facecolor='none', linewidth=0.15)
                ax.add_feature(srtm_contour_feature, zorder=9)      
                
                # Add regions
                group_shp = cartopy.io.shapereader.Reader(rgiO1_shp_fn)
                group_feature = cartopy.feature.ShapelyFeature(group_shp.geometries(), cartopy.crs.PlateCarree(),
                                                               edgecolor='black', facecolor='none', linewidth=2)
                ax.add_feature(group_feature,zorder=10)
                
    #            # Add glaciers
    #            rgi_glac_shp = cartopy.io.shapereader.Reader(rgi_glac_shp_fn)
    #            rgi_glac_feature = cartopy.feature.ShapelyFeature(rgi_glac_shp.geometries(), cartopy.crs.PlateCarree(),
    #                                                              edgecolor='black', facecolor='none', linewidth=0.15)
    #            ax.add_feature(rgi_glac_feature, zorder=9)
    #            
                                                    
                # Add colorbar
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm._A = []
                plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.01)
                fig.text(1, 0.5, var_label, va='center', ha='center', rotation='vertical', size=labelsize)
        
                ax.pcolormesh(lons, lats, var_change, cmap=cmap, norm=norm, zorder=2, alpha=0.8)            
                
                # Title
                ax.set_title(gcm_name + ' ' + rcp + ' (2070-2100 vs 2000-2030)')
                
                # Save figure
                fig.set_size_inches(6,4)
                fig_fn = gcm_name + '_' + rcp + '_' + vn + '.png'
                fig.savefig(figure_fp + fig_fn, bbox_inches='tight', dpi=300)
                plt.close()
                
                
#%% TIME SERIES OF SUBPLOTS FOR EACH GROUP
if option_plot_cmip5_normalizedchange == 1:
    vns = ['volume_glac_annual']
#    vns = ['runoff_glac_monthly']
    
    figure_fp = input.output_sim_fp + 'figures/'
    option_plot_individual_gcms = 0
    
    # Load glaciers
    main_glac_rgi, main_glac_hyps, main_glac_icethickness = load_glacier_data(regions)
    # Groups
    groups, group_cn = select_groups(grouping, main_glac_rgi)
    #%%
    
    if grouping == 'watershed':
        groups.remove('Irrawaddy')
        groups.remove('Yellow')

    multimodel_linewidth = 2
    alpha=0.2
    
    
    reg_legend = []
    num_cols_max = 4
    if len(groups) < num_cols_max:
        num_cols = len(groups)
    else:
        num_cols = num_cols_max
    num_rows = int(np.ceil(len(groups)/num_cols))
        
    for vn in vns:
        fig, ax = plt.subplots(num_rows, num_cols, squeeze=False, sharex=False, sharey=True,
                               figsize=(5*num_rows,4*num_cols), gridspec_kw = {'wspace':0, 'hspace':0})
        add_group_label = 1
        #%%
        for rcp in rcps:
#        for rcp in ['rcp45']:
            ds_multimodels = [[] for group in groups]
            if vn == 'volume_glac_annual':
                masschg_multimodels = [[] for group in groups]
            
            for ngcm, gcm_name in enumerate(gcm_names):
#            for ngcm, gcm_name in enumerate(['GISS-E2-R']):
#                print(ngcm, gcm_name)
            
                # Merge all data, then select group data
                for region in regions:  
#                for region in [13]:                        
                    # Load datasets
                    ds_fn = ('R' + str(region) + '_' + gcm_name + '_' + rcp + '_c2_ba' + str(input.option_bias_adjustment) +
                             '_100sets_2000_2100--subset.nc')
                    ds = xr.open_dataset(netcdf_fp_cmip5 + ds_fn)
  
                    # Bypass GCMs that are missing a rcp scenario
                    try:
                        ds = xr.open_dataset(netcdf_fp_cmip5 + ds_fn)
                    except:
                        continue
                    # Extract time variable
                    time_values_annual = ds.coords['year_plus1'].values
                    time_values_monthly = ds.coords['time'].values
                    # Extract data
                    vn_glac_region = ds[vn].values[:,:,0]
                    vn_glac_std_region = ds[vn].values[:,:,1]
                    
#                    A = vn_glac_std_region
                    
#                    print('ADD ANNUAL RUNOFF STANDARD DEVIATION! DELETE ME!')
                    
                    print(rcp, gcm_name, region, np.min(vn_glac_region.sum(axis=0)))
                    
                    
                    # Convert monthly values to annual
                    if vn == 'runoff_glac_monthly':
                        vn_glac_region = gcmbiasadj.annual_sum_2darray(vn_glac_region)
                        time_values_annual = time_values_annual[:-1]
                        
                        vn_glac_std_region = gcmbiasadj.annual_sum_2darray(vn_glac_std_region)
#                        print('adjust std')
                        

                    # Merge datasets
                    if region == regions[0]:
                        vn_glac_all = vn_glac_region
                        vn_glac_std_all = vn_glac_std_region                        
                    else:
                        vn_glac_all = np.concatenate((vn_glac_all, vn_glac_region), axis=0)
                        vn_glac_std_all = np.concatenate((vn_glac_std_all, vn_glac_std_region), axis=0)                    
                    try:
                        ds.close()
                    except:
                        continue
                    
                # Cycle through groups  
                row_idx = 0
                col_idx = 0
                for ngroup, group in enumerate(groups):
#                for ngroup, group in enumerate([groups[1]]):
                    # Set subplot position
                    if (ngroup % num_cols == 0) and (ngroup != 0):
                        row_idx += 1
                        col_idx = 0
                        
                    # Select subset of data
                    group_glac_indices = main_glac_rgi.loc[main_glac_rgi[group_cn] == group].index.values.tolist()
                    vn_glac = vn_glac_all[group_glac_indices,:]
                    vn_glac_std = vn_glac_std_all[group_glac_indices,:]
                    vn_glac_var = vn_glac_std **2
                     
                    # Plot data
                    if vn == 'volume_glac_annual':
                        # Regional mean, standard deviation, and variance
                        #  mean: E(X+Y) = E(X) + E(Y)
                        #  var: Var(X+Y) = Var(X) + Var(Y) + 2*Cov(X,Y)
                        #    assuming X and Y are indepdent, then Cov(X,Y)=0, so Var(X+Y) = Var(X) + Var(Y)
                        #  std: std(X+Y) = (Var(X+Y))**0.5
                        vn_reg = vn_glac.sum(axis=0)
                        vn_reg_var = vn_glac_var.sum(axis=0)
                        vn_reg_std = vn_reg_var**0.5
                        vn_reg_stdhigh = vn_reg + vn_reg_std
                        vn_reg_stdlow = vn_reg - vn_reg_std
                        # Regional normalized volume           
                        vn_reg_norm = vn_reg / vn_reg[0]
                        vn_reg_norm_stdhigh = vn_reg_stdhigh / vn_reg[0]
                        vn_reg_norm_stdlow = vn_reg_stdlow / vn_reg[0]
                        vn_reg_plot = vn_reg_norm.copy()
                        vn_reg_plot_stdlow = vn_reg_norm_stdlow.copy()
                        vn_reg_plot_stdhigh = vn_reg_norm_stdhigh.copy()
                        
                        # Mass change for text on plot
                        #  Gt = km3 ice * density_ice / 1000
                        #  divide by 1000 because density of ice is 900 kg/m3 or 0.900 Gt/km3
                        vn_reg_masschange = (vn_reg[-1] - vn_reg[15]) * input.density_ice / 1000
                        
#                    elif ('prec' in vn) or ('temp' in vn):       
#                        # Regional mean function (monthly data)
#                        reg_mean_temp_biasadj, reg_mean_prec_biasadj = (
#                                select_region_climatedata(gcm_name, rcp, main_glac_rgi))
#                        # Annual region mean
#                        if 'prec' in vn:
#                            reg_var_mean_annual = reg_mean_prec_biasadj.reshape(-1,12).sum(axis=1)
#                        elif 'temp' in vn:
#                            reg_var_mean_annual = reg_mean_temp_biasadj.reshape(-1,12).mean(axis=1)
#                        # Plot data
#                        vn_reg_plot = reg_var_mean_annual.copy()
                    elif vn == 'runoff_glac_monthly':
                        # Regional mean, standard deviation, and variance
                        #  mean: E(X+Y) = E(X) + E(Y)
                        #  var: Var(X+Y) = Var(X) + Var(Y) + 2*Cov(X,Y)
                        #    assuming X and Y are indepdent, then Cov(X,Y)=0, so Var(X+Y) = Var(X) + Var(Y)
                        #  std: std(X+Y) = (Var(X+Y))**0.5
                        vn_reg = vn_glac.sum(axis=0)
                        vn_reg_var = vn_glac_var.sum(axis=0)
                        vn_reg_std = vn_reg_var**0.5
                        vn_reg_stdhigh = vn_reg + vn_reg_std
                        vn_reg_stdlow = vn_reg - vn_reg_std
                        # Runoff from 2000 - 2017
                        t1_idx = np.where(time_values_annual == 2000)[0][0]
                        t2_idx = np.where(time_values_annual == 2017)[0][0]
                        vn_reg_2000_2017_mean = vn_reg[t1_idx:t2_idx+1].sum() / (t2_idx - t1_idx + 1)
                        # Regional normalized volume        
                        vn_reg_norm = vn_reg / vn_reg_2000_2017_mean
                        vn_reg_norm_stdhigh = vn_reg_stdhigh / vn_reg_2000_2017_mean
                        vn_reg_norm_stdlow = vn_reg_stdlow / vn_reg_2000_2017_mean
                        vn_reg_plot = vn_reg_norm.copy()
                        vn_reg_plot_stdlow = vn_reg_norm_stdlow.copy()
                        vn_reg_plot_stdhigh = vn_reg_norm_stdhigh.copy()

                    # ===== Plot =====                    
                    if option_plot_individual_gcms == 1:
                        ax[row_idx, col_idx].plot(time_values_annual, vn_reg_plot, color=rcp_colordict[rcp], 
                                                  linewidth=1, alpha=alpha, label=None, zorder=1)
                    
                    if rcp == 'rcp45':
                        if group == 'Brahmaputra':
                            print(gcm_name, np.min(vn_reg_plot))
    #                    # Volume change uncertainty
    #                    if vn == 'volume_glac_annual':
    #                        ax[row_idx, col_idx].fill_between(
    #                                time_values, vn_reg_plot_stdlow, vn_reg_plot_stdhigh, 
    #                                facecolor=gcm_colordict[gcm_name], alpha=0.15, label=None)
                    
                    # Group labels
#                    ax[row_idx, col_idx].set_title(title_dict[group], size=14)
                    if add_group_label == 1:
                        ax[row_idx, col_idx].text(0.5, 0.99, title_dict[group], size=14, horizontalalignment='center', 
                                                  verticalalignment='top', transform=ax[row_idx, col_idx].transAxes)
                                
                    # Tick parameters
                    ax[row_idx, col_idx].tick_params(axis='both', which='major', labelsize=25, direction='inout')
                    ax[row_idx, col_idx].tick_params(axis='both', which='minor', labelsize=15, direction='inout')
                    # X-label
                    ax[row_idx, col_idx].set_xlim(time_values_annual.min(), time_values_annual.max())
                    ax[row_idx, col_idx].xaxis.set_tick_params(labelsize=14)
                    ax[row_idx, col_idx].xaxis.set_major_locator(plt.MultipleLocator(50))
                    ax[row_idx, col_idx].xaxis.set_minor_locator(plt.MultipleLocator(10))
                    if col_idx == 0 and row_idx == num_rows-1:
                        ax[row_idx, col_idx].set_xticklabels(['','2000','2050','2100'])
                    elif row_idx == num_rows-1:
                        ax[row_idx, col_idx].set_xticklabels(['','','2050','2100'])
                    else:
                        ax[row_idx, col_idx].set_xticklabels(['','','',''])
                    #  labels are the first one, 2000, 2050, 2100, and 2101
                    # Y-label
                    ax[row_idx, col_idx].yaxis.set_tick_params(labelsize=14)
#                    ax[row_idx, col_idx].yaxis.set_major_locator(MaxNLocator(prune='both'))
                    if vn == 'volume_glac_annual':
#                        if option_plot_individual_gcms == 1:
#                            ax[row_idx, col_idx].set_ylim(0,1.35)
                        ax[row_idx, col_idx].yaxis.set_major_locator(plt.MultipleLocator(0.2))
                        ax[row_idx, col_idx].yaxis.set_minor_locator(plt.MultipleLocator(0.1))
                    elif vn == 'runoff_glac_annual':
                        ax[row_idx, col_idx].set_ylim(0,2)
                        ax[row_idx, col_idx].yaxis.set_major_locator(plt.MultipleLocator(0.5))
                        ax[row_idx, col_idx].yaxis.set_minor_locator(plt.MultipleLocator(0.1))
                        ax[row_idx, col_idx].set_yticklabels(['','','0.5','1.0','1.5', ''])
                    elif vn == 'temp_glac_annual':
                        ax[row_idx, col_idx].yaxis.set_major_locator(plt.MultipleLocator())
                        ax[row_idx, col_idx].yaxis.set_minor_locator(plt.MultipleLocator())
                    elif vn == 'prec_glac_annual':
                        ax[row_idx, col_idx].yaxis.set_major_locator(plt.MultipleLocator())
                        ax[row_idx, col_idx].yaxis.set_minor_locator(plt.MultipleLocator())
                    
                    # Count column index to plot
                    col_idx += 1
                    
                    # Record data for multi-model stats
                    if ngcm == 0:
                        ds_multimodels[ngroup] = [group, vn_reg_plot]
                    else:
                        ds_multimodels[ngroup][1] = np.vstack((ds_multimodels[ngroup][1], vn_reg_plot))
                    
                    if vn == 'volume_glac_annual':
                        if ngcm == 0:
    #                        print(group, rcp, gcm_name, vn_reg_masschange)
                            masschg_multimodels[ngroup] = [group, vn_reg_masschange]
                        else:
    #                        print(group, rcp, gcm_name, vn_reg_masschange)
                            masschg_multimodels[ngroup][1] = np.vstack((masschg_multimodels[ngroup][1], 
                                                                       vn_reg_masschange))
                        
                        
                # Only add group label once
                add_group_label = 0
            
            if vn == 'temp_glac_annual' or vn == 'prec_glac_annual':
                skip_fill = 1
            else:
                skip_fill = 0
            
            # Multi-model mean
            row_idx = 0
            col_idx = 0
            for ngroup, group in enumerate(groups):
                if (ngroup % num_cols == 0) and (ngroup != 0):
                    row_idx += 1
                    col_idx = 0
                # Multi-model statistics
                vn_multimodel_mean = ds_multimodels[ngroup][1].mean(axis=0)
                vn_multimodel_std = ds_multimodels[ngroup][1].std(axis=0)
                vn_multimodel_stdlow = vn_multimodel_mean - vn_multimodel_std
                vn_multimodel_stdhigh = vn_multimodel_mean + vn_multimodel_std
                ax[row_idx, col_idx].plot(time_values_annual, vn_multimodel_mean, color=rcp_colordict[rcp], 
                                          linewidth=multimodel_linewidth, label=rcp, zorder=3)
                if skip_fill == 0:
                    ax[row_idx, col_idx].fill_between(time_values_annual, vn_multimodel_stdlow, vn_multimodel_stdhigh, 
                                                      facecolor=rcp_colordict[rcp], alpha=0.2, label=None,
                                                      zorder=2)  
                   
                # Add mass change to plot
                if vn == 'volume_glac_annual':
                    masschg_multimodel_mean = masschg_multimodels[ngroup][1].mean(axis=0)[0]
                
                    print(group, rcp, np.round(masschg_multimodel_mean,0),'Gt', 
                          np.round((vn_multimodel_mean[-1] - 1)*100,0), '%')
                
                if vn == 'volume_glac_annual' and rcp == rcps[-1]:
                    masschange_str = '(' + str(masschg_multimodel_mean).split('.')[0] + ' Gt)'
                    if grouping == 'all':
                        ax[row_idx, col_idx].text(0.5, 0.93, masschange_str, size=12, horizontalalignment='center', 
                                                  verticalalignment='top', transform=ax[row_idx, col_idx].transAxes, 
                                                  color=rcp_colordict[rcp])
                    else:
                        ax[row_idx, col_idx].text(0.5, 0.88, masschange_str, size=12, horizontalalignment='center', 
                                                  verticalalignment='top', transform=ax[row_idx, col_idx].transAxes, 
                                                  color=rcp_colordict[rcp])
                # Adjust subplot column index
                col_idx += 1
                
        # RCP Legend
        rcp_lines = []
        for rcp in rcps:
            line = Line2D([0,1],[0,1], color=rcp_colordict[rcp], linewidth=multimodel_linewidth)
            rcp_lines.append(line)
        rcp_labels = [rcp_dict[rcp] for rcp in rcps]
        if vn == 'temp_glac_annual' or vn == 'prec_glac_annual':
            legend_loc = 'upper left'
        else:
            legend_loc = 'lower left'
        ax[0,0].legend(rcp_lines, rcp_labels, loc=legend_loc, fontsize=12, labelspacing=0, handlelength=1, 
                       handletextpad=0.5, borderpad=0, frameon=False, title='RCP')
        
#        # GCM Legend
#        gcm_lines = []
#        for gcm_name in gcm_names:
#            line = Line2D([0,1],[0,1], linestyle='-', color=gcm_colordict[gcm_name])
#            gcm_lines.append(line)
#        gcm_legend = gcm_names.copy()
#        fig.legend(gcm_lines, gcm_legend, loc='center right', title='GCMs', bbox_to_anchor=(1.06,0.5), 
#                   handlelength=0, handletextpad=0, borderpad=0, frameon=False)
        
        # Y-Label
        if len(groups) == 1:
            fig.text(-0.01, 0.5, vn_dict[vn], va='center', rotation='vertical', size=14)
        else:
            fig.text(0.03, 0.5, vn_dict[vn], va='center', rotation='vertical', size=16)
#        fig.text(0.03, 0.5, 'Normalized\nVolume [-]', va='center', ha='center', rotation='vertical', size=16)
#        fig.text(0.03, 0.5, 'Normalized\nGlacier Runoff [-]', va='center', ha='center', rotation='vertical', size=16)
        
        # Save figure
        if len(groups) == 1:
            fig.set_size_inches(4, 4)
        else:
            fig.set_size_inches(7, num_rows*2)
#        if option_plot_individual_gcms == 1:
#            figure_fn = grouping + '_' + vn + '_wgcms_' + str(len(gcm_names)) + 'gcms_' + str(len(rcps)) +  'rcps.png'
#        else:
        figure_fn = grouping + '_' + vn + '_' + str(len(gcm_names)) + 'gcms_' + str(len(rcps)) +  'rcps.png'
                
        
        fig.savefig(figure_fp + figure_fn, bbox_inches='tight', dpi=300)    
            
            
            
            
#%%
# Regional maps
if option_region_map_nodata == 1:
    figure_fp = netcdf_fp_cmip5 + '../figures/'
    grouping = 'rgi_region'
    
    east = 104
    west = 65
    south = 26.5
    north = 45
    xtick = 5
    ytick = 5
    xlabel = 'Longitude [$^\circ$]'
    ylabel = 'Latitude [$^\circ$]'
    
    labelsize = 13
    
    colorbar_dict = {'precfactor':[0,5],
                     'tempchange':[-5,5],
                     'ddfsnow':[0.0036,0.0046],
                     'dif_masschange':[-0.1,0.1]}

    # Add group and attribute of interest
    if grouping == 'rgi_region':
        group_shp = cartopy.io.shapereader.Reader(rgiO1_shp_fn)
        group_shp_attr = 'RGI_CODE'
    elif grouping == 'watershed':
        group_shp = cartopy.io.shapereader.Reader(watershed_shp_fn)
        group_shp_attr = 'watershed'
    elif grouping == 'kaab':
        group_shp = cartopy.io.shapereader.Reader(kaab_shp_fn)
        group_shp_attr = 'Name'
    
    # Load glaciers
    main_glac_rgi, main_glac_hyps, main_glac_icethickness = load_glacier_data(regions)
    
    # Groups
    groups, group_cn = select_groups(grouping, main_glac_rgi)

    # Create the projection
    fig, ax = plt.subplots(1, 1, figsize=(10,5), subplot_kw={'projection':cartopy.crs.PlateCarree()})
    # Add country borders for reference
    ax.add_feature(cartopy.feature.BORDERS, alpha=0.15, zorder=10)
    ax.add_feature(cartopy.feature.COASTLINE)
    # Set the extent
    ax.set_extent([east, west, south, north], cartopy.crs.PlateCarree())    
    # Label title, x, and y axes
    ax.set_xticks(np.arange(east,west+1,xtick), cartopy.crs.PlateCarree())
    ax.set_yticks(np.arange(south,north+1,ytick), cartopy.crs.PlateCarree())
    ax.set_xlabel(xlabel, size=labelsize)
    ax.set_ylabel(ylabel, size=labelsize)
    
#    # Add contour lines
#    srtm_contour_shp = cartopy.io.shapereader.Reader(srtm_contour_fn)
#    srtm_contour_feature = cartopy.feature.ShapelyFeature(srtm_contour_shp.geometries(), cartopy.crs.PlateCarree(),
#                                                          edgecolor='black', facecolor='none', linewidth=0.15)
#    ax.add_feature(srtm_contour_feature, zorder=2)  

    # Add attribute of interest to the shapefile
    for rec in group_shp.records():
        # plot polygon outlines on top of everything with their labels
        ax.add_geometries(rec.geometry, cartopy.crs.PlateCarree(), facecolor='None', 
                          edgecolor='black', linewidth=2, zorder=3)
    for group in groups:
        print(group, title_location[group][0])
        ax.text(title_location[group][0], 
                title_location[group][1], 
                title_dict[group], horizontalalignment='center', size=12, zorder=4)
        if group == 'Karakoram':
            ax.plot([72.2, 76.2], [34.3, 35.8], color='black', linewidth=1.5)
        elif group == 'Pamir':
            ax.plot([69.2, 73], [37.3, 38.3], color='black', linewidth=1.5)     
    
    # Save figure
    fig.set_size_inches(6,4)
    fig_fn = grouping + '_only_map.png'
    fig.savefig(figure_fp + fig_fn, bbox_inches='tight', dpi=300)
    
 
#%%
if option_glaciermip_table == 1:
#    vn = 'massbaltotal_glac_monthly'
    startyear = 2000
    endyear = 2100
    
    output_fp = input.output_sim_fp + 'GlacierMIP/'
    if os.path.exists(output_fp) == False:
        os.makedirs(output_fp)
    
    # Load glaciers
    main_glac_rgi, main_glac_hyps, main_glac_icethickness = load_glacier_data(regions)
    # Groups
    groups, group_cn = select_groups(grouping, main_glac_rgi)
    

    # Load mass balance data
    ds_all = {}
    for rcp in rcps:
#    for rcp in ['rcp26']:
        ds_all[rcp] = {}
        for ngcm, gcm_name in enumerate(gcm_names):
#        for ngcm, gcm_name in enumerate(['CanESM2']):
        
            print(rcp, gcm_name)
            
            # Merge all data, then select group data
            for region in regions:      
                
                # Load datasets
                ds_fn = ('R' + str(region) + '_' + gcm_name + '_' + rcp + '_c2_ba' + str(input.option_bias_adjustment) +
                         '_100sets_2000_2100--subset.nc')
                ds = xr.open_dataset(netcdf_fp_cmip5 + ds_fn)
  
                # Bypass GCMs that are missing a rcp scenario
                try:
                    ds = xr.open_dataset(netcdf_fp_cmip5 + ds_fn)
                except:
                    continue
                
                # Extract time variable
                time_values_annual = ds.coords['year_plus1'].values
                time_values_monthly = ds.coords['time'].values
                # Extract start/end indices for calendar year!
                time_values_df = pd.DatetimeIndex(time_values_monthly)
                time_values = np.array([x.year for x in time_values_df])
                time_idx_start = np.where(time_values == startyear)[0][0]
                time_idx_end = np.where(time_values == endyear)[0][0]
                year_idx_start = np.where(time_values_annual == startyear)[0][0]
                year_idx_end = np.where(time_values_annual == endyear)[0][0]
                
                time_values_annual_subset = time_values_annual[year_idx_start:year_idx_end+1]
                vol_glac_region = ds['volume_glac_annual'].values[:,year_idx_start:year_idx_end+1,0]

                # Merge datasets
                if region == regions[0]:
                    vol_glac_all = vol_glac_region
                else:
                    vol_glac_all = np.concatenate((vol_glac_all, vol_glac_region), axis=0)
                try:
                    ds.close()
                except:
                    continue
            
            ds_all[rcp][gcm_name] = {}
            for ngroup, group in enumerate(groups):
                # Sum volume change for group
                group_glac_indices = main_glac_rgi.loc[main_glac_rgi[group_cn] == group].index.values.tolist()
                volchg_group = vol_glac_all[group_glac_indices,:].sum(axis=0)

                ds_all[rcp][gcm_name][group] = volchg_group

    #%%    
    # Export csv files
    output_cns = ['year'] + gcm_names
    
    summary_cns = []
    for rcp in rcps:
        cn_mean = rcp + '-mean'
        cn_std = rcp + '-std'
        cn_min = rcp + '-min'
        cn_max = rcp + '-max'
        summary_cns.append(cn_mean)
        summary_cns.append(cn_std)
        summary_cns.append(cn_min)
        summary_cns.append(cn_max)
    output_summary = pd.DataFrame(np.zeros((len(groups),len(summary_cns))), index=groups, columns=summary_cns)
    

    for group in groups:
        for rcp in rcps:
            
            print(group, rcp)
            
            output = pd.DataFrame(np.zeros((len(time_values_annual_subset), len(output_cns))), columns=output_cns)
            output['year'] = time_values_annual_subset
            
            for gcm_name in gcm_names:
                output[gcm_name] = ds_all[rcp][gcm_name][group]
            
            # Export csv file
            if grouping == 'rgi_region':
                grouping_prefix = 'R'
            else:
                grouping_prefix = ''
            output_fn = ('GlacierMIP_' + grouping_prefix + str(group) + '_' + rcp + '_' + str(startyear) + '-' + 
                         str(endyear) + '_volume_km3ice.csv')
            
            output.to_csv(output_fp + output_fn, index=False)
            
            vol_data = output[gcm_names].values
            vol_remain_perc = vol_data[-1,:] / vol_data[0,:] * 100
            
            rcp_cns = [rcp + '-mean', rcp+'-std', rcp+'-min', rcp+'-max']
            output_summary.loc[group, rcp_cns] = [vol_remain_perc.mean(), vol_remain_perc.std(), vol_remain_perc.min(), 
                                                  vol_remain_perc.max()]
            
    # Export summary
    output_summary_fn = ('GlacierMIP_' + grouping + '_summary_' + str(startyear) + '-' + str(endyear) + 
                         '_volume_remaining_km3ice.csv')
    output_summary.to_csv(output_fp + output_summary_fn)
            