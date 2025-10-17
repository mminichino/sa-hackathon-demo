##

provider "rediscloud" {
  api_key    = var.api_key
  secret_key = var.secret_key
}

module "essentials" {
  source      = "git::https://github.com/mminichino/terraform.git//redis/cloud/modules/essentials?ref=v1.0.45"
  name        = var.name
  cloud       = var.cloud
  region      = var.region
  plan        = var.plan
  persistence = var.persistence
}
