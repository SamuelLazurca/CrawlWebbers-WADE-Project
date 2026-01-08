from app.core.sparql import run_sparql
from app.models.schemas import DatasetSchema

def datasets_get_all_query() -> list[DatasetSchema]:
    query = """
    PREFIX : <http://example.org/ontology/vulnerability#>
    
    SELECT ?dataset ?label ?datasetID ?datasetURL ?infoHash ?sizeInBytes 
           ?addedDate ?datasetType ?numberOfFiles ?numberOfDownloads ?uploadedByLabel ?uploadedByURL
    WHERE {
        ?dataset a :Dataset ;
                 rdfs:label ?label ;
                 :datasetID ?datasetID ;
                 :datasetURL ?datasetURL ;
                 :infoHash ?infoHash ;
                 :sizeInBytes ?sizeInBytes ;
                 :addedDate ?addedDate ;
                 :datasetType ?datasetType ;
                 :numberOfFiles ?numberOfFiles ;
                 :numberOfDownloads ?numberOfDownloads ;
                 :uploadedBy ?uploadedBy .
        
        ?uploadedBy rdfs:label ?uploadedByLabel ;
                    schema:url ?uploadedByURL .
    }
    """
    
    rows = run_sparql(query)
    datasets = []
    for row in rows:
        datasets.append(DatasetSchema(
            id=row["datasetID"]["value"],
            name=row["label"]["value"],
            url=row["datasetURL"]["value"],
            info_hash=row["infoHash"]["value"],
            size_in_bytes=int(row["sizeInBytes"]["value"]),
            added_date=row["addedDate"]["value"],
            dataset_type=row["datasetType"]["value"],
            number_of_files=int(row["numberOfFiles"]["value"]),
            number_of_downloads=int(row["numberOfDownloads"]["value"]),
            uploaded_by=row["uploadedByLabel"]["value"],
            uploaded_by_url=row["uploadedByURL"]["value"]
        ))
    return datasets

def dataset_get_by_id_query(dataset_id) -> DatasetSchema | None:
    query = """
    PREFIX : <http://example.org/ontology/vulnerability#>
    
    SELECT ?dataset ?label ?datasetID ?datasetURL ?infoHash ?sizeInBytes 
           ?addedDate ?datasetType ?numberOfFiles ?numberOfDownloads ?uploadedByLabel ?uploadedByURL
    WHERE {
        ?dataset a :Dataset ;
                 rdfs:label ?label ;
                 :datasetID ?datasetID ;
                 :datasetURL ?datasetURL ;
                 :infoHash ?infoHash ;
                 :sizeInBytes ?sizeInBytes ;
                 :addedDate ?addedDate ;
                 :datasetType ?datasetType ;
                 :numberOfFiles ?numberOfFiles ;
                 :numberOfDownloads ?numberOfDownloads ;
                 :uploadedBy ?uploadedBy .
        
        ?uploadedBy rdfs:label ?uploadedByLabel ;
                    schema:url ?uploadedByURL .
        
        FILTER(?datasetID = "%s")
    }
    """
    
    rows = run_sparql(query % dataset_id)
    for row in rows:
        return DatasetSchema(
            id=row["datasetID"]["value"],
            name=row["label"]["value"],
            url=row["datasetURL"]["value"],
            info_hash=row["infoHash"]["value"],
            size_in_bytes=int(row["sizeInBytes"]["value"]),
            added_date=row["addedDate"]["value"],
            dataset_type=row["datasetType"]["value"],
            number_of_files=int(row["numberOfFiles"]["value"]),
            number_of_downloads=int(row["numberOfDownloads"]["value"]),
            uploaded_by=row["uploadedByLabel"]["value"],
            uploaded_by_url=row["uploadedByURL"]["value"]
        )
    return None