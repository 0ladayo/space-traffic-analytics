import dlt
import pandas as pd
import logging
import pubsub_utils
import functions_framework



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Ingestion Script started ...')


@dlt.resource(table_name = 'orbital_satellites_data', write_disposition = 'replace', file_format = 'parquet')
def load_satellites_data():
    urls = ['https://celestrak.com/NORAD/elements/gp.php?GROUP=active&FORMAT=csv', 
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-1408-debris&FORMAT=csv',
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=fengyun-1c-debris&FORMAT=csv',
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-33-debris&FORMAT=csv',
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=csv',
    ]
    
    labels = ['Active', 'Debris (Cosmos 1408)', 'Debris (Fengyun 1C)', 'Debris (Iridium 33)', 'Debris (Cosmos 2251)']

    dtypes = {
        'MEAN_MOTION_DDOT': float, 
        'MEAN_MOTION_DOT': float,  
        'BSTAR': float,           
        'ECCENTRICITY': float,     
        'MEAN_MOTION': float,
        'INCLINATION': float,
        'RA_OF_ASC_NODE': float,
        'ARG_OF_PERICENTER': float,
        'MEAN_ANOMALY': float,
    }

    for index, url in enumerate(urls):
        logging.info(f'fetching data from {url}...')
        for chunk in pd.read_csv(url, chunksize = 100, dtype = dtypes):
            chunk['TYPE'] = labels[index]
            yield chunk

@functions_framework.http
def main(request):
    try:
        pipeline = dlt.pipeline(pipeline_name = 'orbital_telemetry_pipeline', destination = 'bigquery', dataset_name = "orbital_satellites_dataset",
        staging = 'filesystem')
        load_info = pipeline.run(load_satellites_data)
        logging.info(f'Ingestion pipeline finished successfully. Info: {load_info}')
        pubsub_utils.publish_message()
        return 'Success', 200

    except Exception:
        logging.exception('Ingestion pipeline crashed')
        return 'Failed', 500