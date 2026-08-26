resource "aws_key_pair" "deployer" {
  key_name   = "aws-3tier-key"
  public_key = file("~/.ssh/aws-3tier-key.pub")
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "ansible" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ansible.id]
  key_name               = aws_key_pair.deployer.key_name

  tags = {
    Name = "3tier-ansible-server"
  }
}

resource "aws_instance" "frontend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.frontend.id]
  key_name               = aws_key_pair.deployer.key_name

  tags = {
    Name = "3tier-frontend-server"
  }
}

resource "aws_instance" "backend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.private_backend.id
  vpc_security_group_ids = [aws_security_group.backend.id]
  key_name               = aws_key_pair.deployer.key_name
  iam_instance_profile   = aws_iam_instance_profile.backend_profile.name  

  tags = {
    Name = "3tier-backend-server"
  }
}

resource "aws_instance" "database" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.private_db.id
  vpc_security_group_ids = [aws_security_group.database.id]
  key_name               = aws_key_pair.deployer.key_name

  tags = {
    Name = "3tier-database-server"
  }
}

resource "aws_instance" "jenkins" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.small"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.jenkins.id]
  key_name               = aws_key_pair.deployer.key_name

  tags = {
    Name = "3tier-jenkins-server"
  }
}
