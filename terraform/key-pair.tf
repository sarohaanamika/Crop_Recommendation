resource "aws_key_pair" "crop_app" {
  key_name   = "${var.project_name}-key-pair"
  public_key = file("~/.ssh/crop-app-key.pub")  # Use the new public key
  
  tags = {
    Name = "${var.project_name}-key-pair"
  }
}