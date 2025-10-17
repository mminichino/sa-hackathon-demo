##

variable "name" {
  type = string
}

variable "api_key" {
  type = string
}

variable "secret_key" {
  type = string
}

variable "cloud" {
  type    = string
  default = "GCP"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "plan" {
  type    = string
  default = "Single-Zone_Persistence_5GB"
}

variable "persistence" {
  type    = string
  default = "aof-every-1-second"
}
