import arcpy
import os
import tempfile
from numpy import trapz

frt = r'C:\Users\jcruz\Documents\ArcGIS\Default.gdb\frestes_prueba'


def overlap(fc):
    temp_dir = tempfile.mkdtemp()
    temp_gdb = "temp.gdb"
    arcpy.CreateFileGDB_management(temp_dir, temp_gdb)
    gdb= os.path.join(temp_dir, temp_gdb)
    arcpy.CreateFeatureDataset_management(gdb, "for_topo", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision")
    dataset = os.path.join(gdb,"for_topo")
    arcpy.CreateTopology_management(dataset, "topo_frts", "")
    # Process: Feature Vertices To Points
    arcpy.FeatureVerticesToPoints_management(fc, os.path.join(dataset,'frt_ends'), "END")
    # Process: Add Feature Class To Topology
    topology= os.path.join(dataset,'topo_frts')
    arcpy.AddFeatureClassToTopology_management(topology, os.path.join(dataset,'frt_ends'), "1", "1")
    # Process: Add Rule To Topology
    arcpy.AddRuleToTopology_management(topology, "Must Be Disjoint (Point)",  os.path.join(dataset,'frt_ends'), "", "", "")
    # Process: Validate Topology
    arcpy.ValidateTopology_management(topology, "Full_Extent")
    # Process: Export Topology Errors
    arcpy.ExportTopologyErrors_management(topology, dataset, "topo_frts")

    topo_frts_point = os.path.join(dataset,"topo_frts_point")
    topo_frts_line = os.path.join(dataset,"topo_frts_line")
    topo_frts_poly = os.path.join(dataset,"topo_frts_poly")
    
    count_errors= arcpy.GetCount_management(topo_frts_point)
    if count_errors > 0:
        arcpy.AddWarning("Los frentes analizados tienen Errores\nde superposicion de vertices finales")
        arcpy.CopyFeatures_management(topo_frts_point,os.path.join(os.path.dirname(fc),'errores_point2'))
    else:
        arcpy.AddMessage("Los frentes analizados no tienen Errores\nde superposicion de vertices finales")
    try:
        del temp_dir
    except:
        pass


def op_direction(fc):
    line_points={}

    def coords(fc2):
        idmzns = []
        pts = []
        dict_idmzns = {}
        old_idmzn = ''
        with arcpy.da.SearchCursor(fc2, ['SHAPE@', 'FRENTE_ORD', 'UBIGEO', 'ZONA', 'MANZANA'], sql_clause= (None, "ORDER BY UBIGEO, ZONA, MANZANA ASC")) as lines:
            for line in lines:
                x_i = line[0].firstPoint.X
                y_i = line[0].firstPoint.Y
                x_f = line[0].lastPoint.X
                y_f = line[0].lastPoint.Y
                xy = (x_i,y_i, x_f, y_f)
                idmzn = line[2]+line[3]+line[4]
                # print (idmzn)
                if idmzn not in idmzns and len(pts)==0:
                    idmzns.append(idmzn)
                    pts.append(xy)
                elif idmzn in idmzns:
                    old_idmzn= idmzn
                    pts.append(xy)
                elif idmzn not in idmzns and len(pts) > 0:
                    dict_idmzns[old_idmzn]=pts
                    pts=[]
                    idmzns.append(idmzn)
                    pts.append(xy)
        # print(idmzns)
        # print(pts, len(pts))
        return dict_idmzns

    def area_pol(xy):
        x_i = xy[0]
        y_i = xy[1]
        x_f = xy[2]
        y_f = xy[3]
        area = ((x_f-x_i)*(y_f-y_i))/2 + (x_f-x_i)*y_i
        return area

    re_idmzn ={}
    for i in coords(fc):
        lista_areas=[]
        for a in coords(fc)[i]:
            lista_areas.append(area_pol(a))
        re_idmzn[i]=sum(lista_areas)
    print (re_idmzn)
            #line_points[int(line[1])] = (x_i,y_i, x_f, y_f)
    #return coords(fc)

def frtcontinue(fc):
    pass

#overlap(frt)
print (op_direction(frt))

print ('fin')