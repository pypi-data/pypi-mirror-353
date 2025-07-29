resource "aws_ecr_repository" "labels_test" {
  name                 = "labels/test"
  image_tag_mutability = "IMMUTABLE"

  tags = {
    "Name"              = "labels.ecr"
    "fluidattacks:line" = "cost"
    "fluidattacks:comp" = "labels"
  }
}
