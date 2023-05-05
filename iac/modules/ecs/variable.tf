variable "common" {
  type = object({
    app_name = string
    env       = string
  })
}

variable "network" {
  type = object({
    vpc_id             = string
    private_subnet_ids = list(string)
  })
}

variable "task" {
  type = object({
    family                = string
    cpu                   = string
    memory                = string
    container_definitions = list(any)
  })
}