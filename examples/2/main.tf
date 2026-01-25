/*
 * This examples demonstrates the ability of the tool to detect redundant
 * depends_on across a chain of implicit dependencies. The instance already
 * depends on the VPC through the subnet, but an explicit depends_on is still
 * added.
 */

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_instance" "example" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id

  depends_on = [aws_vpc.main]
}
