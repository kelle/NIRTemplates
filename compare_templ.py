''' 
This procedure compares spectra to NIR L templates, either Alejandro's txt files or Adam's fits files.
'''

def separate_bands(spec, bandnames, bandlimits):
    '''
    This function separates a spectrum by bands as described in bandlimits.
    *spec*
      The spectrum as a numpy array
    *bandnames*
      List with the names of the bands, in the order desired.
    *bandlimits*
    Dictionary with bandname keys containing a list with float numbers specifying the bands limits (e.g. {'J': [0.8,1.4], 'H': [1.4,1.9], 'K': [1.9,2.4]}
    '''
    import numpy as np
    
    specSep = [None] * 3
    for bIdx, band in enumerate(bandnames):
        bLim = bandlimits[band][0]
        bMax = bandlimits[band][1]
        
        idx1 = np.where(spec[0,:] >= bLim)
        idx2 = np.where(spec[0,:] <= bMax)
        idx = np.intersect1d(idx1[0], idx2[0])
        if len(idx) == 0:
            print 'Error in spectrum range.'
            return
        specSep[bIdx] = spec[:,idx]
        
    return specSep


def plotspec(specData, bandNames, limits, objID, plotInstructions, plotInput=None):
    # Plots set of spectral data and saves plots in a PDF file.
    # specData and limits must be dictionaries.
    
    import numpy
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import types
    
    # 1) Check data consistency ===============================================
    try:
        specData.keys()
    except AttributeError:
        print 'Spectra not received as dictionaries.'
        return
    try:
        limits.keys()
    except AttributeError:
        print 'Limits not received as dictionaries.'
        return
    
    # 2) Initialize variables and color sets to use in plots ==================
    GRAYS = ['#585858', '#686868', '#707070', '#808080', '#909090', \
             '#A0A0A0', '#B0B0B0', '#C0C0C0', '#D0D0D0', '#E0E0E0']
    COLOR_SET = numpy.array(['#CC3333','#FF0000','#CC0000','#990000','#CC3300', \
                             '#FF3333','#FF6699','#FF3399','#CC0099','#FF0066', \
                             '#663300','#CC9900','#FFCC33','#666600','#669966', \
                             '#666666','#99CC99','#66CC99','#CCFF00','#66FF33', \
                             '#009933','#006600','#003300','#000066','#3333FF', \
                             '#99FFFF','#00FFFF','#33CCFF','#3399CC','#0066FF'])
                # 0-plum, 1-red, 2-indian red, 3-maroon, 4-brick,
                # 5-tomato, 6-salmon, 7-fuchsia, 8-deep pink, 9-pink,
                # 10-brown, 11-chocolate, 12-wheat, 13-dk olive, 14-olive,
                # 15-silver, 16-lt green, 17-aquamarine, 18-yellow green, 19-lime,
                # 20-green, 21-forest, 22-dk green, 23-navy, 24-blue
                # 25-sky blue, 26-lt blue, 27-orchid, 28-steel blue, 29-royal blue
    colors = [None] * 16
    colors[15] = COLOR_SET[[1,3,6,7,10,11,12,18,19,20,21,24,25,27,29]].tolist()
    colors[14] = COLOR_SET[[1,3,6,7,11,12,18,19,20,21,24,25,27,29]].tolist()
    colors[13] = COLOR_SET[[1,3,6,7,11,12,19,20,21,24,25,27,29]].tolist()
    colors[12] = COLOR_SET[[1,3,6,7,11,12,19,20,21,25,27,29]].tolist() 
    colors[11] = COLOR_SET[[1,3,6,11,12,19,20,21,25,27,29]].tolist()
    colors[10] = COLOR_SET[[1,6,11,12,19,20,21,25,27,29]].tolist()
    colors[9]  = COLOR_SET[[1,6,11,12,19,20,25,27,29]].tolist()
    colors[8]  = COLOR_SET[[1,6,11,12,19,20,25,29]].tolist()
    colors[7]  = COLOR_SET[[1,6,11,19,20,25,29]].tolist()
    colors[6]  = COLOR_SET[[1,6,11,20,25,29]].tolist()
    colors[5]  = COLOR_SET[[1,6,11,20,29]].tolist()
    colors[4]  = COLOR_SET[[1,11,20,29]].tolist()
    colors[3]  = COLOR_SET[[1,20,29]].tolist()
    colors[2]  = COLOR_SET[[1,29]].tolist()
    colors[1]  = COLOR_SET[[1]].tolist()
    
    numColors = len(specData['J']) / 2
    plotColors = colors[numColors][:]
    plotColors.reverse()    
    BLACK = '#000000'
    GRAY  = '#CCCCCC'
    WHITE = '#FFFFFF'
    RED   = '#FF0000'
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$) + constant'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    if numColors <= 8:
        figHeight = 7
        txtSize = 7
    else:
        txtSize = 9
        figHeight = 8.6
    plt.rc('font', size=txtSize)
    fig = plt.figure(1, figsize=(7.33, figHeight))
    plt.clf()
    
    # 4) Generate Subplots ====================================================
    bandNames.reverse()
    for bandIdx, band in enumerate(bandNames):
        
        # 4.1) If band data is only one set, convert it into array of sets ----
        if specData[band][0] is not None:
            if len(specData[band][0]) > 6:
                specData[band] = [specData[band],]
        
        # 4.2) Initialize variables -------------------------------------------
        spLines = []
        minPlot = 1
        maxPlot = 1
        copyColors = list(plotColors)
        
        # 4.3) Initialize Subplot ---------------------------------------------
        tmpLeft = 0.06 + (2 - bandIdx) * 0.32
        subPlot = plt.figure(1).add_subplot(1,3,3 - bandIdx, \
                            position=[tmpLeft,0.07,0.265,0.89])
                                   # [left,bottom,width,height]
        subPlot.set_autoscale_on(False)
        
        # Create dummy axes instance to be able to later manipulate upper axis
        #ax2 = subPlot.axes.twiny()
        
        # Set figure and axes labels (on left-most subplot)
        if bandIdx == 2:
            subPlot.set_xlabel(X_LABEL, position=(1.65,0.08), fontsize=9)
            subPlot.set_ylabel(Y_LABEL, fontsize=9)
        
        # 4.4) Plot spectra ---------------------------------------------------
        offset = 0
        for specIdx, spec in enumerate(specData[band]):
            if spec is None:
                continue
            
            # Define plot parameters
            plotType = plotInstructions[specIdx]
            lnStyle = '-'
            objLabel = objID[specIdx]
            if plotType == 'target':
                plotColor = BLACK
                lnWidth = 0.8
            elif plotType == 'template':
                plotColor = copyColors.pop()
                lnWidth = 0.7
            if specIdx > 0 and specIdx % 2 == 0:
                if bandIdx == 0:
                    offset = offset + 0.55
                elif bandIdx == 1:
                    offset = offset + 0.75
                else:
                    offset = offset + 1
            
            wls = np.array(spec[0])
            fluxes = np.array(spec[1])
            
            # Plot spectral strip when available
            if plotType == 'template' and len(spec) > 3:
                errs = np.array(spec[2])
                mins = np.array(spec[3])
                maxs = np.array(spec[4])
                
                for wlIdx, wl in enumerate(wls):
                    # Skip first and last points
                    if wlIdx == 0:
                        continue
                    elif wlIdx == len(wls) - 1:
                        continue
                    elif not numpy.isfinite(mins[wlIdx]):
                        continue
                    
                    # Set location of lower left corner of rectangle
                    rect_x = wl - ((wl - wls[wlIdx - 1]) / 2)
                    rect_y = mins[wlIdx] + offset
                    
                    # Set dimensions of rectangle
                    rect_width = ((wl - wls[wlIdx - 1]) / 2) + \
                                 ((wls[wlIdx + 1] - wl) / 2)
                    rect_height = maxs[wlIdx] - mins[wlIdx]
                    
                    # Set color fill of rectangle
                    err = errs[wlIdx]
                    if err > 0.19:
                        grayIdx = 9
                    elif err > 0.17:
                        grayIdx = 8
                    elif err > 0.16:
                        grayIdx = 7
                    elif err > 0.15:
                        grayIdx = 6
                    elif err > 0.13:
                        grayIdx = 5
                    elif err > 0.11:
                        grayIdx = 4
                    elif err > 0.09:
                        grayIdx = 3
                    elif err > 0.07:
                        grayIdx = 2
                    elif err > 0.06:
                        grayIdx = 1
                    else:
                        grayIdx = 0
                    rect_color = GRAYS[grayIdx]
                    
                    # Add rectangle to plot
                    rect_patch = mpatches.Rectangle(xy=(rect_x, rect_y), \
                                                    width=rect_width, \
                                                    height=rect_height, color=rect_color)
                    subPlot.add_patch(rect_patch)
            
            # Plot spectral lines
            subPlot.plot(wls, fluxes + offset, color=plotColor, linestyle=lnStyle, \
                    dash_joinstyle='round', linewidth=lnWidth, label=objLabel, \
                    drawstyle='steps-mid')
            
            # Plot a dummy line on secondary axis to later modify upper x-axis
            #if specIdx == 0:
            #    ax2.plot(wls,[-0.5] * len(wls), color=WHITE)
                
            # Track the highest & lowest y-axis values to fix y-axis limits later            
            tmpMin = numpy.nanmin(fluxes)
            if tmpMin < minPlot:
                minPlot = tmpMin
            tmpMax = numpy.nanmax(fluxes + offset)
            if tmpMax > maxPlot:
                maxPlot = tmpMax
            
            # Track the highest y-axis value for the tail of each band
            if specIdx % 2 == 0:
                tailMax = numpy.nanmax(fluxes[-8:-1])
            else:
                currMax = numpy.nanmax(fluxes[-8:-1])
                if currMax > tailMax:
                    tailMax = currMax
            
            # Add annotation to template plot
            if specIdx % 2 == 1:
                textLoc = (0, 10)
                annotLoc = (wls[-10], tailMax + offset)
                annotTxt = objLabel
                subPlot.annotate(annotTxt, xy=annotLoc, xycoords='data', \
                                color=BLACK, xytext=textLoc, \
                                 textcoords='offset points')
        
        # 4.5) Fix axes limits ------------------------------------------------
        minPlot = minPlot - minPlot * 0.1
        maxOff = 0.02
        maxPlot = maxPlot + maxPlot * maxOff
        
        plt.ylim(ymin=minPlot, ymax=maxPlot)
        subPlot.set_xlim(xmin=limits[band][0], \
                         xmax=limits[band][1] * 1.001)
        #ax2.set_xlim(xmin=limits[band][0], \
        #                 xmax=limits[band][1] * 1.001)
        
        # 4.6) Customize y axis -----------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # 5) Add legend =======================================================
        if bandIdx == 2:
            xpos = 0.9 # in wavelength units
            ypos = 0.4 # in flux units
            xp = 0.3   # where 0 is left, 0.5 is middle, and 1 is right
            
            # add lines
            subPlot.axhline(y=ypos, xmin=xp, xmax=xp+0.18, color=BLACK)
            subPlot.axhline(y=ypos-0.15, xmin=xp, xmax=xp+0.03, color=colors[10][0])
            subPlot.axhline(y=ypos-0.15, xmin=xp+0.03, xmax=xp+0.06, color=colors[10][2])
            subPlot.axhline(y=ypos-0.15, xmin=xp+0.06, xmax=xp+0.09, color=colors[10][3])
            subPlot.axhline(y=ypos-0.15, xmin=xp+0.09, xmax=xp+0.12, color=colors[10][4])
            subPlot.axhline(y=ypos-0.15, xmin=xp+0.12, xmax=xp+0.15, color=colors[10][5])
            subPlot.axhline(y=ypos-0.15, xmin=xp+0.15, xmax=xp+0.18, color=colors[10][9])
            
            # add texts
            textLgd = 'NIR Templates'
            if grav == 'g':
                textLgd = textLgd + '*'
                explain = r'*L1$\gamma$ template is just one object'
            elif grav == 'b':
                textLgd = textLgd + '*'
                explain = r'*L2$\beta$ and L3$\beta$ templates are just ' \
                          + 'one object'
            else:
                explain = ''
                        
            subPlot.text(xpos, ypos - 0.3, explain, fontsize=5, color=BLACK)
            subPlot.text(xpos + 0.2, ypos - 0.2, textLgd, fontsize=6, color=BLACK)
            subPlot.text(xpos + 0.2, ypos - 0.05, plotInput, fontsize=6, color=BLACK)
        
    return fig

# ============================= PROCEDURE =====================================

# 1. LOAD RELEVANT MODULES ----------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import astrotools as at
from astropy.io import ascii
import sys
import pdb

# 2. SET UP VARIABLES ---------------------------------------------------------
GITUSER = 'alejo'

# Paths
if GITUSER == 'alejo':
    FOLDER_OUT = '/Users/alejo/KCData/Output/compare/'
    FOLDER_TEMPL = '/Users/alejo/KCData/Output/compare/templates/'
elif GITUSER == 'kelle':
    FOLDER_OUT = '/Users/kelle/Dropbox/Analysis/compare/'
    FOLDER_TEMPL = '/Users/kelle/Dropbox/Shared/Kelle-Alejo/templates/'

DELL_CHAR = '\t' # Delimiter character

# Get user input
interestObject = raw_input('enter FITS file name with full path: ').strip()
ObjectName = raw_input('Objects Name: ').strip()
grav = 'f' # raw_input('enter g/b/f to select templates: ').lower()
inputAdam = raw_input('Use Adam`s templates? (y/n; blank=no): ').strip().lower()
if interestObject == '' or grav == '':
    sys.exit(0)
try:
    with open(interestObject): pass
except IOError:
    print 'File not found.'
    sys.exit(0)
if inputAdam == '' or inputAdam == 'n':
    AdamTemplates = False
else:
    AdamTemplates = True

if grav == 'g':
    SP_TYPES = ['L0','L2','L3','L4']
elif grav =='b':
    SP_TYPES = ['L0','L1']
else:
    #SP_TYPES = ['L0']
    SP_TYPES = ['L0','L1','L2','L3','L4','L5','L6','L7','L8']

# Define spectral bands
BANDS = ['J','H','K']
BAND_LIMS = {}.fromkeys(BANDS)
BAND_NORMS = {}.fromkeys(BANDS)
for band in BANDS:
    BAND_LIMS[band] = [None] * 2
    BAND_NORMS[band] = [None] * 2
BAND_LIMS['J'][0] = 0.8
BAND_LIMS['J'][1] = 1.4 
BAND_LIMS['H'][0] = 1.4
BAND_LIMS['H'][1] = 1.9
BAND_LIMS['K'][0] = 1.9
BAND_LIMS['K'][1] = 2.4
BAND_NORMS['J'][0] = 0.87
BAND_NORMS['J'][1] = 1.39
BAND_NORMS['H'][0] = 1.41
BAND_NORMS['H'][1] = 1.89
BAND_NORMS['K'][0] = 1.91
BAND_NORMS['K'][1] = 2.39

# 3. GET SPECTRUM OF TARGET ---------------------------------------------------
specRaw = at.read_spec(interestObject)[0]
specRaw = np.array(specRaw)
if specRaw is None:
    print 'Could not get spectrum from file.'
    sys.exit(0)

# Separate spectrum by bands
specSep = separate_bands(specRaw, BANDS, BAND_LIMS)

# Normalize spectrum
specN = [None] * 3
for bIdx, band in enumerate(BANDS):
    specN[bIdx] = at.norm_spec(specSep[bIdx], BAND_NORMS[band])[0]

if specN[0] is None:
    'Error normalizing spectra.'
    sys.exit(0)

# 4. GET NIR TEMPLATES --------------------------------------------------------
# 4.1 Initialize holder of template spectra and strips
templ = [None] * len(SP_TYPES)
for tp in range(len(SP_TYPES)):
    templ[tp] = [[] for i in range(3)]

# 4.2 Fetch templates
for spIdx, sp in enumerate(SP_TYPES):
    for bdIdx, band in enumerate(BANDS):
        if AdamTemplates:
            fileNm = sp + '_template_'+ band + '.fits'
            templRaw = at.read_spec(FOLDER_TEMPL + fileNm, templ=True, verbose=False)[0]
            templLs = np.array(templRaw) #.tolist()
            # Normalize spectrum
            minIdx = np.where(templLs[0,:] > BAND_NORMS[band][0])[0][0]
            maxIdx = np.where(templLs[0] < BAND_NORMS[band][1])[0][-1]
            templLs[1:,:] = templLs[1:,:] / np.mean(templLs[1][minIdx:maxIdx])
            templLs = templLs.tolist()
        else:
            fileNm = sp + band + '_' + grav + '.txt'
            #if GITUSER == 'alejo':
            #    templRaw = ad.open(FOLDER_TEMPL + fileNm, delimiter=DELL_CHAR)
            #    templLs = np.array(templRaw).tolist()
            #elif GITUSER == 'kelle':
            templRaw = ascii.read(FOLDER_TEMPL + fileNm, format='no_header', delimiter=DELL_CHAR)
            templLs = np.array([templRaw[c].data.tolist() for c in templRaw.colnames])
        templRaw = ''
        templ[spIdx][bdIdx] = templLs

# 5. CONSOLIDATE ALL SPECTRA --------------------------------------------------
# 5.1 Initialize holders of consolidated spectra and headers
spTypes = []
spectra = {}.fromkeys(BANDS)
for band in BANDS:
    spectra[band] = []

# 5.2 Stitch together in a sequence template & target spectra
for spIdx, sp in enumerate(SP_TYPES):
    for bdIdx, band in enumerate(BANDS):
        if templ[spIdx][bdIdx] != []:
            spectra[band].append(templ[spIdx][bdIdx])
            spectra[band].append(specN[bdIdx])
            
            if bdIdx == 0:
                spTypes.append(sp)
                spTypes.append(sp)

for band in BANDS:
    spectra[band].reverse()
spTypes.reverse()

# 6. PLOT ALL SPECTRA ---------------------------------------------------------
plotInstructions = ['target','template'] * (len(spTypes) - 1)
# Add proper identifiers to spectral types labels
if grav == 'g':
    greek = r'$\gamma$'
elif grav == 'b':
    greek = r'$\beta$'
else:
    greek = ''
for sTidx, sT in enumerate(spTypes):
    spTypes[sTidx] = spTypes[sTidx] + greek

figure = plotspec(specData=spectra, bandNames=BANDS, limits=BAND_LIMS, \
                  objID=spTypes, plotInstructions=plotInstructions, \
                  plotInput=ObjectName + ' ' + interestObject)

if AdamTemplates:
    txtadam = '_adam'
else:
    txtadam = ''
plt.savefig(FOLDER_OUT + ObjectName +'_' + grav + txtadam + '.pdf', dpi=600)
print 'wrote: ' + FOLDER_OUT + ObjectName +'_' + grav + txtadam + '.pdf'