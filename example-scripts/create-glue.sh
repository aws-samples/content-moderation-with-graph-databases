#!/bin/bash

# id is the reserved column for vertex tables
# id, from, to are the reserved columns for edge tables

## pass the profile and the endpoint in as variables 
## e.g. default eu-west-2 s3://neptune-overspill/
echo $1;
echo $2;
echo $3; 

s3bucket=$3
dbname='content-mod'

aws glue create-database \
--database-input "{\"Name\":\"${dbname}\"}" \
--profile $1 \
--endpoint https://glue.$2.amazonaws.com


aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"transactionby", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"out", "Type":"string"},
            {"Name":"in", "Type":"string"}                 
            
        ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
             "separatorChar":",",
            "componenttype":"edge"} 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com
    

aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"game", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"gameid", "Type":"string"}, 
            {"Name":"timestamp", "Type":"timestamp"}
                ], 
        "Location": "'$s3bucket'"},
        "Parameters":{ 
            "separatorChar":",",
            "componenttype":"vertex"
            } 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com


aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"player", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"playerid", "Type":"string"}, 
            {"Name":"timestamp", "Type":"timestamp"}
                ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
            "separatorChar":",",
            "componenttype":"vertex"
            } 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com

aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"abuse", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"abuseid", "Type":"string"}, 
            {"Name":"abuseType", "Type":"string"}, 
            {"Name":"abuseContent", "Type":"string"},
            {"Name":"timestamp", "Type":"timestamp"}   
                ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
            "separatorChar":",",
            "componenttype":"vertex"
            } 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com
    
    

aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"transaction", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"transactionid", "Type":"string"}, 
            {"Name":"transactionValue", "Type":"string"},
            {"Name":"playerid", "Type":"string"},
            {"Name":"timestamp", "Type":"timestamp"}   
                ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
            "separatorChar":",",
            "componenttype":"vertex"
            } 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com
        





aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"played", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"duration", "Type":"int"},
            {"Name":"out", "Type":"string"},
            {"Name":"in", "Type":"string"}         
        ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
             "separatorChar":",",
            "componenttype":"edge"} 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com

aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"wasabusive", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"out", "Type":"string"},
            {"Name":"in", "Type":"string"}                 
            
        ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
             "separatorChar":",",
            "componenttype":"edge"} 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com


aws glue create-table \
    --database-name $dbname \
    --table-input  '{"Name":"abuseingame", "StorageDescriptor":{ 
        "Columns":[ 
            {"Name":"id", "Type":"string"}, 
            {"Name":"out", "Type":"string"},
            {"Name":"in", "Type":"string"}                 
            
        ], 
        "Location":"'$s3bucket'"},
        "Parameters":{ 
             "separatorChar":",",
            "componenttype":"edge"} 
        }' \
    --profile $1 \
    --endpoint https://glue.$2.amazonaws.com



