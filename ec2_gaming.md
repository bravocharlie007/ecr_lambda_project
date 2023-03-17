ec2:
create instance
create instance template
create sg (allows rdp and ssh from select ip addresses)
create ebs
create role
install drivers
install steam
install steamcmd
install directx (need to disable Local Server/IF: Enhanced Security Configuration)
create windows profile with lower permissions in ec2


after launch, create image

s3:
create bucket for drivers
create bucket for savegames

OR:
get them from aws s3:
arn:aws:s3:::dcv-license.us-east-1                                                                                          │ Allow  │ s3:GetObject                                                                                                                │ AWS:${CloudGraphicsOnT3S3Read} │           │
│   │ arn:aws:s3:::dcv-license.us-east-1/*                                                                                        │        │ s3:ListBucket                                                                                                               │                                │           │
│   │ arn:aws:s3:::ec2-amd-windows-drivers                                                                                        │        │                                                                                                                             │                                │           │
│   │ arn:aws:s3:::ec2-amd-windows-drivers/*                                                                                      │        │                                                                                                                             │                                │           │
│   │ arn:aws:s3:::nvidia-gaming                                                                                                  │        │                                                                                                                             │                                │           │
│   │ arn:aws:s3:::nvidia-gaming/*

app:
user_apis:
onboard user
start instance
launch instance (maybe admin instead?):
v1: only one instance type
v*: several instance types determined by app in accordance of game needs. Compare rating of recommended GPU of game with that of Ec2). Ability to override.
install videogames for user
launch videogames?
stop instance

admin:
offboard user
terminate instance

Should the user have only access to the game or to steam/the rest of the pc as well? What if the user wants mods?

send weekly invoices/send amounts to venmo via email (Can we programmatically create venmo apis?


identity store?

lambdas:
automate driver installation


How do you turn off inactive instances?
Several users on one instance?

CREATE USER PROFILES IN EC2 INSTANCES (NOT ADMIN)

When instance is stopped:
copy save game to s3: C:\Users\Administrator\Documents\Paradox Interactive\Europa Universalis IV\save games
Create ami
Maybe install drivers?


ssm parameters must follow this template: 
/application/ec2deployer/resource/main/* for any infra resource created in AWS console/by AWS
/application/ec2deployer/resource/terraform/* for any infra resource created by terraform
/application/ec2deployer/user/* for anything user related

tf-user/tf-pave-apply:
Read: 
/application/ec2deployer/resource/*
Write:
/application/ec2deployer/resource/terraform/* 