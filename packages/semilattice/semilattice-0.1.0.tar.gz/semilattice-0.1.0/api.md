# Populations

Types:

```python
from semilattice.types import APIResponsePopulations, Error
```

Methods:

- <code title="post /v1/populations">client.populations.<a href="./src/semilattice/resources/populations.py">create</a>(\*\*<a href="src/semilattice/types/population_create_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_populations.py">APIResponsePopulations</a></code>
- <code title="get /v1/populations/{population_id}">client.populations.<a href="./src/semilattice/resources/populations.py">get</a>(population_id) -> <a href="./src/semilattice/types/api_response_populations.py">APIResponsePopulations</a></code>
- <code title="post /v1/populations/{population_id}/test">client.populations.<a href="./src/semilattice/resources/populations.py">test</a>(population_id) -> <a href="./src/semilattice/types/api_response_populations.py">APIResponsePopulations</a></code>

# Answers

Types:

```python
from semilattice.types import Answer, AnswersRequest, APIResponseAnswers
```

Methods:

- <code title="post /v1/answers/benchmark">client.answers.<a href="./src/semilattice/resources/answers.py">benchmark</a>(\*\*<a href="src/semilattice/types/answer_benchmark_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_answers.py">APIResponseAnswers</a></code>
- <code title="get /v1/answers/{question_id}">client.answers.<a href="./src/semilattice/resources/answers.py">get</a>(question_id) -> <a href="./src/semilattice/types/api_response_answers.py">APIResponseAnswers</a></code>
- <code title="post /v1/answers">client.answers.<a href="./src/semilattice/resources/answers.py">simulate</a>(\*\*<a href="src/semilattice/types/answer_simulate_params.py">params</a>) -> <a href="./src/semilattice/types/api_response_answers.py">APIResponseAnswers</a></code>
