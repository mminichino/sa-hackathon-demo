##

output "endpoint" {
  value = module.essentials.public_endpoint
}

output "password" {
  value     = module.essentials.password
  sensitive = true
}
