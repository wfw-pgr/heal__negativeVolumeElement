import os, sys
import numpy as np

# ========================================================= #
# ===  heal__negativeVolumeElement.py                   === #
# ========================================================= #

def heal__negativeVolumeElement( mode="reverse", inpFile=None, outFile=None, offset=1.0e-6, \
                                 nodes_format=None, reflect=False ):

    flag__makeError = True
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile      is None ): sys.exit( "[heal__negativeVolumeElement.py] inpFile == ???" )
    if ( outFile      is None ): sys.exit( "[heal__negativeVolumeElement.py] outFile == ???" )
    if ( nodes_format is None ): nodes_format == "%15.8e"

    # ------------------------------------------------- #
    # --- [2] load mesh File                        --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.load__meshio as lms
    cells, points = lms.load__meshio( mshFile=inpFile, elementType="tetra", \
                                      returnType="cell-point" )
    if ( flag__makeError ):
        cells[-1,0], cells[-1,1] = cells[-1,1], cells[-1,0]
        cells[-3,0], cells[-3,1] = cells[-3,1], cells[-3,0]
        import nkMeshRoutines.save__nastranFile as snf
        snf.save__nastranFile( points=points, cells=cells, outFile="msh/model_err.msh", \
                               nodes_format=nodes_format )
    cells_        = cells + 1


    # ------------------------------------------------- #
    # --- [3] calculate volume of elements          --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.calculate__tetraVolume as vol
    volumes    = vol.calculate__tetraVolume( elems=cells_, nodes=points )
    index      = np.where( volumes < 0.0 )
    nNegative  = len( index[0] )
    print( "[heal__negativVolumeElement.py] nNegative :: {0} ".format( nNegative ) )

    if ( nNegative == 0 ):
        print( "[heal__negativVolumeElement.py] No negative volume... [END] " )
        return()
    
    # ------------------------------------------------- #
    # --- [4] negative volume healing               --- #
    # ------------------------------------------------- #
    illegalies = cells[index]
    volumes    = volumes[index]
    if   ( mode.lower() == "modify"  ):
        points = modify__element( nodes=points, illegalies=illegalies, \
                                  volumes=volumes, offset=offset )
    elif ( mode.lower() == "reverse" ):
        cells  = reverse__element( elems=cells, index=index )
    
    # ------------------------------------------------- #
    # --- [5] save nastran bdf file                 --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.save__nastranFile as snf
    snf.save__nastranFile( points=points, cells=cells, outFile=outFile, \
                           nodes_format=nodes_format )
    return()



# ========================================================= #
# ===  modify__element                                  === #
# ========================================================= #
def modify__element( nodes=None, illegalies=None, volumes=None, offset=None, reflect=False ):
    
    e1_,e2_,e3_,e4_ = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( illegalies is None ): sys.exit( "[reverse__element] illegalies == ???" )
    if ( nodes      is None ): sys.exit( "[reverse__element] nodes      == ???" )
    if ( volumes    is None ): sys.exit( "[reverse__element] volumes    == ???" )
    if ( offset     is None ): sys.exit( "[reverse__element] offset     == ???" )

    illegalies_ = illegalies + 1
    nIllegal    = illegalies.shape[0]
    
    # ------------------------------------------------- #
    # --- [2] update nodes                          --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.calculate__tetraFaceArea as tfa
    areas = tfa.calculate__tetraFaceArea( elems=illegalies, nodes=nodes )
    for ik in range( nIllegal ):
        ivertex  = np.argmax( areas[ik,:] )
        overtex  = list( set( [0,1,2,3] ) - set( [ivertex] ) )
        v1       = nodes[ illegalies[ik,overtex[1]],:] - nodes[ illegalies[ik,overtex[0]],:]
        v2       = nodes[ illegalies[ik,overtex[2]],:] - nodes[ illegalies[ik,overtex[0]],:]
        v3       = nodes[ illegalies[ik,ivertex   ],:] - nodes[ illegalies[ik,overtex[0]],:]
        nvec     = np.cross( v1, v2 )
        nhat     = np.cross( v1, v2 ) / np.linalg.norm( nvec )
        sign     = np.sign( np.dot( v3, nhat ) )
        height   = 3.0 * volumes[ik] / areas[ik,ivertex]
        if ( reflect ):
            move = offset + 2.0*height
        else:
            move = offset
        new_node = move * ( -1.0 ) * sign * nhat[:] + nodes[ illegalies[ik,ivertex],:]
        nodes[ illegalies[ik,ivertex],:] = np.copy( new_node )
    return( nodes )


# ========================================================= #
# ===  reverse__element                                 === #
# ========================================================= #
def reverse__element( elems=None, index=None ):

    e1_,e2_,e3_,e4_ = 0, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( elems is None ): sys.exit( "[reverse__element] elems == ???" )
    if ( index is None ): sys.exit( "[reverse__element] index == ???" )

    # ------------------------------------------------- #
    # --- [2] swap element position                 --- #
    # ------------------------------------------------- #
    for ik in index:
        elem_t        = elems[ik,e1_]
        elems[ik,e1_] = elems[ik,e2_]
        elems[ik,e2_] = elem_t
        
    return( elems )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #
if ( __name__=="__main__" ):
    offset  = 1.e-6
    mode    = "modify"
    inpFile = "msh/model.bdf"
    outFile = "msh/model_mod.bdf"
    heal__negativeVolumeElement( mode=mode, inpFile=inpFile, outFile=outFile )
