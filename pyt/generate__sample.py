import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  geometry                                    === #
# ========================================================= #

def make__geometry():
    
    gmsh.model.occ.addBox( -0.5, -0.5, -0.5, \
		           +1.0, +1.0, +1.0 )
    gmsh.model.occ.addBox( +0.0,  0.0,  0.0, \
		           +1.0, +1.0, +1.0 )
    return()

    


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    make__geometry()
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    meshFile = "dat/mesh.conf"
    physFile = "dat/phys.conf"
    import nkGmshRoutines.assign__meshsize as ams
    meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile )
    
    # gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    # gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    import nkMeshRoutines.convert__gmsh2nastran as g2n
    g2n.convert__gmsh2nastran( inpFile="msh/model.msh", outFile="msh/model.bdf", \
                               nodes_format=None )
    gmsh.finalize()
    

