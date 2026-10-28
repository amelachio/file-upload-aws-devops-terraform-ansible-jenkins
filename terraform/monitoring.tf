resource "aws_cloudwatch_metric_alarm" "jenkins_disk_high" {
  alarm_name          = "3tier-jenkins-disk-above-80"
  alarm_description   = "Disque racine de Jenkins utilise a plus de 80 %"
  namespace           = "CWAgent"
  metric_name         = "disk_used_percent"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.jenkins.id
    path       = "/"
    device     = "nvme0n1p1"
    fstype     = "ext4"
  }
}
