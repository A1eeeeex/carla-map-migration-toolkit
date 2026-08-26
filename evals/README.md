# Evaluations

`trigger/cases.json` is a static, reviewable expectation set. The same positive
prompt is an adjacent-route negative for the other two Skills. Out-of-scope and
ambiguous prompts apply to all three Skills.

The repository tests dataset shape and expected route coverage. Actual model
trigger precision/recall is environment-owned work and must remain `NOT_RUN`
until a supported eval runner records its model, configuration, date, and raw
results.
