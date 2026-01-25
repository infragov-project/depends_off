// modules/app/main.tf

variable "subnet_id" {
  type = string
}

resource "aws_instance" "server" {
  ami                    = "ami-123"
  instance_type          = "t2.micro"
  subnet_id              = var.subnet_id
}
