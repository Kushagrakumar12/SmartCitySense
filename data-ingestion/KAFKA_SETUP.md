# 🚀 Kafka Setup Guide

This guide will help you set up Apache Kafka locally to stream events from the data ingestion system.

## 📋 Prerequisites

- macOS (you're using this)
- Homebrew installed
- Terminal access

---

## 🔧 Installation

### Step 1: Install Kafka using Homebrew

```bash
# Install Kafka (includes Zookeeper)
brew install kafka
```

This installs:
- Kafka broker
- Zookeeper (required for Kafka)
- Command-line tools

### Step 2: Verify Installation

```bash
# Check if Kafka is installed
kafka-topics --version

# Should show something like: 3.6.0 or similar
```

---

## 🚀 Starting Kafka

Kafka requires two services: **Zookeeper** and **Kafka Broker**

### Method 1: Using Homebrew Services (Recommended)

```bash
# Start Zookeeper
brew services start zookeeper

# Start Kafka
brew services start kafka

# Verify they're running
brew services list
```

You should see both services with status "started".

### Method 2: Manual Start (For Development)

Open **two terminal windows**:

**Terminal 1 - Zookeeper:**
```bash
zookeeper-server-start /opt/homebrew/etc/kafka/zookeeper.properties
```

**Terminal 2 - Kafka:**
```bash
kafka-server-start /opt/homebrew/etc/kafka/server.properties
```

Keep both terminals running!

---

## ✅ Verify Kafka is Running

### Create Test Topic

```bash
# Create the citypulse_events topic
kafka-topics --create \
  --topic citypulse_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### List Topics

```bash
# Should show 'citypulse_events'
kafka-topics --list --bootstrap-server localhost:9092
```

### Test Producer

```bash
# Send a test message
echo "test message" | kafka-console-producer \
  --broker-list localhost:9092 \
  --topic citypulse_events
```

### Test Consumer

```bash
# Read messages from the topic
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic citypulse_events \
  --from-beginning
```

You should see your test message appear!

Press `Ctrl+C` to exit.

---

## 🧪 Test with Data Ingestion System

Now that Kafka is running, test the pipeline:

```bash
cd /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion

# Run one-time ingestion
python main.py --mode once
```

You should now see:
- ✅ Events collected: 25
- ✅ Events sent: 25  (instead of 0)
- ✅ Success rate: 100% (instead of 0%)

---

## 👀 Monitor Events in Real-Time

In a separate terminal, run a Kafka consumer to watch events as they arrive:

```bash
# Watch events in real-time
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic citypulse_events \
  --from-beginning \
  --property print.key=true \
  --property print.timestamp=true
```

Then run the ingestion:
```bash
python main.py --mode once
```

You'll see all 25 events streaming through Kafka!

---

## 🛑 Stopping Kafka

### If using Homebrew Services:

```bash
# Stop Kafka
brew services stop kafka

# Stop Zookeeper
brew services stop zookeeper

# Verify they're stopped
brew services list
```

### If running manually:

Press `Ctrl+C` in both terminal windows.

---

## 🔄 Restart Kafka

```bash
# Using Homebrew services
brew services restart zookeeper
brew services restart kafka

# Or manually start again
```

---

## 📊 Useful Kafka Commands

### Topic Management

```bash
# List all topics
kafka-topics --list --bootstrap-server localhost:9092

# Describe a topic
kafka-topics --describe --topic citypulse_events --bootstrap-server localhost:9092

# Delete a topic
kafka-topics --delete --topic citypulse_events --bootstrap-server localhost:9092
```

### Consumer Groups

```bash
# List consumer groups
kafka-consumer-groups --list --bootstrap-server localhost:9092

# Describe a consumer group
kafka-consumer-groups --describe --group my-group --bootstrap-server localhost:9092
```

### Check Messages

```bash
# Count messages in topic
kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic citypulse_events
```

---

## 🐛 Troubleshooting

### "Connection refused" Error

**Problem:** Kafka/Zookeeper not running

**Solution:**
```bash
# Check if services are running
brew services list

# Start if needed
brew services start zookeeper
brew services start kafka

# Wait 10 seconds, then test
kafka-topics --list --bootstrap-server localhost:9092
```

### "NoBrokersAvailable" Error

**Problem:** Kafka broker hasn't fully started

**Solution:**
```bash
# Wait 10-15 seconds after starting Kafka
# Then try again
```

### Port Already in Use

**Problem:** Another process using Kafka's ports (9092 or 2181)

**Solution:**
```bash
# Find process using port 9092
lsof -i :9092

# Kill the process
kill -9 <PID>

# Restart Kafka
brew services restart kafka
```

### Can't Create Topic

**Problem:** Insufficient permissions or Kafka not fully started

**Solution:**
```bash
# Check Kafka logs
tail -f /opt/homebrew/var/log/kafka/server.log

# Look for errors
```

---

## 📁 Configuration Files

Kafka configuration files location:
- Zookeeper: `/opt/homebrew/etc/kafka/zookeeper.properties`
- Kafka: `/opt/homebrew/etc/kafka/server.properties`

### Useful Settings (server.properties)

```properties
# Port Kafka listens on
listeners=PLAINTEXT://localhost:9092

# Where Kafka stores data
log.dirs=/opt/homebrew/var/lib/kafka-logs

# How long to keep messages (7 days)
log.retention.hours=168
```

---

## 🎯 Quick Start Commands

```bash
# Start everything
brew services start zookeeper
brew services start kafka

# Create topic
kafka-topics --create \
  --topic citypulse_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Test ingestion
cd /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion
python main.py --mode once

# Watch events
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic citypulse_events \
  --from-beginning
```

---

## ✅ Success Checklist

- [ ] Kafka and Zookeeper installed via Homebrew
- [ ] Both services started and running
- [ ] Topic `citypulse_events` created
- [ ] Test message sent and received
- [ ] Data ingestion system sends events successfully
- [ ] Can monitor events with console consumer

---

## 🚀 Next Steps

Once Kafka is running:
1. Run continuous ingestion: `python main.py --mode scheduled --interval 5`
2. Monitor events in real-time with consumer
3. Share the Kafka topic with Person 2 (stream processing)
4. Set up Kafka monitoring (optional)

---

## 💡 Pro Tips

1. **Keep Kafka running:** Use Homebrew services for auto-start on boot
2. **Monitor disk space:** Kafka stores messages on disk
3. **Adjust retention:** Modify `log.retention.hours` based on needs
4. **Use consumer groups:** For parallel processing downstream
5. **Check logs:** `/opt/homebrew/var/log/kafka/` for debugging

---

## 🆘 Still Having Issues?

Common issues and solutions:

1. **Java not installed?**
   ```bash
   brew install openjdk@17
   ```

2. **Kafka won't start?**
   ```bash
   # Clear Kafka data and restart
   rm -rf /opt/homebrew/var/lib/kafka-logs/*
   brew services restart zookeeper
   brew services restart kafka
   ```

3. **Can't connect from Python?**
   - Check `localhost:9092` is accessible
   - Verify firewall settings
   - Try `127.0.0.1:9092` instead

---

You're now ready to stream events to Kafka! 🎉
