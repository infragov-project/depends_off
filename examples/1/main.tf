/*
 * This example demonstrates one of the simplest redundant `depends_on` usages.
 * Note how the subnet already depends on the VPC through the `vpc_id`
 * attribute, but an explicit `depends_on` is still added.
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
  depends_on = [aws_vpc.main]
}
