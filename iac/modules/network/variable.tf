variable "common" {
  type = object({
    app_name = string
    env    = string
    region = string
  })
}

variable "network" {
  type = object({
    cidr = string
    public_subnets = list(object({
      az   = string
      cidr = string
    }))

    private_subnets = list(object({
      az   = string
      cidr = string
    }))
  })
}

