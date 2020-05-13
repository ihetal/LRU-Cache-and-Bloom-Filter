# LRU Cache and Bloom Filter

The assignment 3 is based on our simple [distributed cache](https://github.com/sithu/cmpe273-spring20/tree/master/midterm) where you have implmented the GET and PUT operations.

## 1. DELETE operation

You will be adding the DELETE operation to delete entires from the distributed cache.

_Request_

```json
{ 
    'operation': 'DELETE',
    'id': 'hash_code_of_the_object',
}
```

_Response_

```json
{
    'success'
}
```

## 2. LRU Cache

In order to reduce unnecessary network calls to the servers, you will be adding LRU cache on client side. On each GET call, you will be checking against data from a local cache.

Implement LRU cache as Python decorator and you can pass cache size as argument. You must name the name as lru_cache.py and can be tested via test_lru_cache.py.

```python
@lru_cache(5)
def get(...):
    ...
    return ...
    

def put(...):
    ...
    return ...

def delete(...):
    ...
    return ...

```

@lru_cache is your implementation as a decorator function and do NOT use any existing LRU libraries. 

> Although you do not need to print execution time __[0.00000191s]__ and cache hit logs __[cache-hit]__, you should able to run test_lru_cache.py successfully without any errors in order to get full credits.

## 3. Bloom Filter

Finally, you will be implementing a bloom filter so that we can validate any key lookup without hitting the servers. The bloom filter will have two operations:

### Add

This add() function handles adding new key to the membership set.

### Is_member

This is_member() function checks whether a given key is in the membership or not.

On the client side, the GET and DELETE will invoke is_member(key) function first prior to calling the servers while the PUT and DELETE will call add(key) function to update the membership.

Bit array and hash libraries:

```
pipenv install bitarray
pipenv install mmh3
```

Use this formula to calculate Bit array size:

```
m = - (n * log(p)) / (log(2)^2) 

```

where,
- m = bit array size
- n = number of expected keys to be stored
- p = Probability of desired false positive rate

Answer the following question:

* What are the best _k_ hashes and _m_ bits values to store one million _n_ keys (E.g. e52f43cd2c23bb2e6296153748382764) suppose we use the same MD5 hash key from [pickle_hash.py](https://github.com/sithu/cmpe273-spring20/blob/master/midterm/pickle_hash.py#L14) and explain why?

```python
@lru_cache(5)
def get(key):
    if bloomfilter.is_member(key):
        return udp_client.get(key)
    else:
        return None

def put(key, value):
    bloomfilter.add(key)
    return udp_client.put(key, value)

def delete(key):
    if bloomfilter.is_member(key):
        return udp_client.delete(key)
    else:
        return None

```

You can validate your implementation using _test_bloom_filter.py_ and should get the expected output as test_bloom_filter_output.txt .





