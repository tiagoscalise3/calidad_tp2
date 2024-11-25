
import pandas as pd 

produccion_convencional = pd.read_csv("produccin-de-pozos-de-gas-y-petrleo-2024.csv.crdownload")
pozos = pd.read_csv("capitulo-iv-pozos.csv")
produccion_no_convencionales= pd.read_csv("produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv")

connvencional_con_prod = produccion_convencional[(produccion_convencional['prod_pet'] > 0) | (produccion_convencional['prod_gas'] > 0) ]
convencional_sin_prod = produccion_convencional[(produccion_convencional['prod_pet'] <= 0) & (produccion_convencional['prod_gas'] <= 0) ]

produccion_no_convencionales = produccion_no_convencionales[(produccion_no_convencionales['anio'] == 2024)]
no_convencional_con_prod = produccion_no_convencionales[((produccion_no_convencionales['prod_pet'] > 0) | (produccion_no_convencionales['prod_gas'] > 0)) ]
no_convencional_sin_prod = produccion_no_convencionales[(produccion_no_convencionales['prod_pet'] <= 0) & (produccion_no_convencionales['prod_gas'] <= 0) ]
                        
convencional_no_convencional = produccion_convencional[produccion_convencional['tipo_de_recurso'] == 'NO CONVENCIONAL']                        

columnas_diferentes = produccion_no_convencionales.columns.difference(convencional_no_convencional.columns)


produccion_no_convencionales_sin_ubicaciones  = produccion_no_convencionales.drop(columns = columnas_diferentes)

produccion_no_convencionales_sin_ubicaciones_ordenada = produccion_no_convencionales_sin_ubicaciones.sort_values(by=['idpozo','fecha_data']).reset_index(drop=True)
convencional_no_convencional_ordenada = convencional_no_convencional.sort_values(by=['idpozo','fecha_data']).reset_index(drop=True)

iguales = produccion_no_convencionales_sin_ubicaciones_ordenada.equals(convencional_no_convencional_ordenada)

diferencias = convencional_no_convencional_ordenada.ne(produccion_no_convencionales_sin_ubicaciones_ordenada)

#%%
from inline_sql import sql 
import json

pozo_no_convencional = pozos[pozos['tipo_recurso'] == 'NO CONVENCIONAL'].reset_index(drop = True)


pozo_no_convencional['geojson'] = pozo_no_convencional['geojson'].apply(json.loads)



pozo_no_convencional['coordenadax'] = pozo_no_convencional['geojson'].apply(lambda x: x['coordinates'][0])
pozo_no_convencional['coordenaday'] = pozo_no_convencional['geojson'].apply(lambda x: x['coordinates'][1])
pozo_no_convencional.drop('geojson',axis = 1 ,inplace=True)

 

consulta = """SELECT *,
        CASE
            WHEN (produccion_no_convencionales.coordenadax = pozo_no_convencional.coordenadax) AND (produccion_no_convencionales.coordenaday = pozo_no_convencional.coordenaday) THEN 'Igual'
            ELSE 'Diferente'
        END AS ubicacion_igual
    FROM produccion_no_convencionales
    INNER JOIN pozo_no_convencional
    ON  produccion_no_convencionales.idpozo = pozo_no_convencional.idpozo
    """

coordenadas_iguales = sql^ consulta

verdad = coordenadas_iguales[coordenadas_iguales['ubicacion_igual'] == 'Diferente']

