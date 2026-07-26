# test 1

curl -s -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the second person to walk on the moon?"}'

echo

curl -s http://127.0.0.1:5000/history
echo

# test 2

curl -s -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the 3 person to walk on the moon?"}'

echo

curl -s http://127.0.0.1:5000/history
echo

# test 3

curl -s -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the 1 person to walk on the sun?"}'

echo

curl -s http://127.0.0.1:5000/history
echo

# test 4

curl -s -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the 10000 person to walk on the moon?"}'

echo

curl -s http://127.0.0.1:5000/history
echo