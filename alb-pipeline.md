Creates an alb in public subnet in peripheral (i.e. non central) account
Creates a sg for alb
In the central DNS account, adds an Alias A record called mipp.dev.awsbeta.jpmchase.net for the dev.awsbeta.jpmchase.net domain which points to the alb dns in us-east-1 with failover value PRIMARY
Inputs: hosted zone id of the alb, alb dns name, record type, alias (True)
The lambdas verify who is the record owner in the central account
In the central DNS account, adds an Alias A record called mipp.dev.awsbeta.jpmchase.net for the dev.awsbeta.jpmchase.net domain in eu-west-2 with failover value SECONDARY



change_batch_payload for route53 client:
{
    'Comment': 'My Comment',
    'Changes': [{
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': '\\100.mipp.dev.awsbeta.jpmchase.net',
                'Type': 'A',
                'AliasTarget': {
                    'HostedZoneId': 'Hosted Zone Id of the ALB',
                    'DNSName': 'DNS Name of ALB',
                    'EvaluateTargetHealth': False
                },
                'GeoLocation': {
                    'ContinentCode': 'NA'
                },
                'SetIdentifier': 'GEOLOCATION-2661d528-c4'
            }
        }, {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': '\\100.mipp.dev.awsbeta.jpmchase.net',
                'Type': 'TXT',
                'ResourceRecords': [{
                        'Value': '"accountId=2680;"'
                    }
                ],
                'TTL': 300
            }
        }
    ]
}
