import numpy as np
import heal__negativeVolumeElement           as hnv
import nkMeshRoutines.calculate__tetraVolume as vol
import nkBasicAlgs.execute__commands         as exe

# ========================================================= #
# ===  autoheal__negativeElement.py                     === #
# ========================================================= #

def autoheal__negativeElement():

    # ------------------------------------------------- #
    # --- [1] load constants                        --- #
    # ------------------------------------------------- #
    import nkUtilities.load__constants as lcn
    cnsFile = "dat/unified.conf"
    const   = lcn.load__constants( inpFile=cnsFile )

    # ------------------------------------------------- #
    # --- [2] heal mesh File                        --- #
    # ------------------------------------------------- #
    for offset in const["mesh.autoheal.offsets"]:
        heal__negativeVolumeElement( mode   =const["mesh.autoheal.mode"], inpFile=inpFile, \
                                     outFile=inpFile.replace( ".bdf", "_.bdf" ), \
                                     offset =offset, nodes_format=const["mesh.nastran.format"], \
                                     reflect=const["mesh.autoheal.reflect"] )
        import nkMeshRoutines.load__meshio as lms
        cells, points = lms.load__meshio( mshFile=inpFile.replace( ".bdf", "_.bdf" ), \
                                          elementType="tetra", \
                                          returnType="cell-point" )
        cells_     = cells + 1
        volumes    = vol.calculate__tetraVolume( elems=cells_, nodes=points )
        index      = np.where( volumes < 0.0 )
        nNegative  = len( index[0] )
        print( "[heal__negativVolumeElement.py] nNegative :: {0} ".format( nNegative ) )
    
        if ( nNegative == 0 ):
            print( "[heal__negativVolumeElement.py] No negative volume... [END] " )
            break
        if ( const["mesh.autoheal.mode"] == "reverse" ):
            print( "[heal__negativeVolumeElement.py] No need to iterate reverse mode... " )
            break

    commands = [ "mv {0} {1}".format( inpFile.replace( ".bdf", "_.bdf" ), inpFile ) ]
    exe.execute__commands( commands=commands )
        

# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    autoheal__negativeElement()
