---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: ''
assignees: ''

---

**Is your feature request related to an existing Ready Player Me pyblish plugin?**  
Mention plugin here.

**Is your feature request related to a problem? Please describe.**  
A clear and concise description of what the problem is.

**Describe the solution you'd like**  
A clear and concise description of what you want to happen. Ideally, use Gherkin syntax.
Example:

```Gherkin
Feature: Action to make all materials single-sided
  Let users quickly make _all_ materials single-sided, regardless of validation state.

  Rule: Make all materials single-sided
    Background:
      Given I have materials

    Example: two-sided materials
      Given I have run the validation
      And at least one of the materials is two-sided
      When I choose the single-sided materials action in the validator
      Then all materials are single-sided

    Example: one-sided materials
      Given I have run the validation
      And there are no two-sided materials
      Then I still have the option to make all materials one-sided
  ...
```

**Describe the impact**  
Gauge how much __impact__ this feature would have for its users [e.g. how much time it will save].
What is its value?

**Describe alternatives you've considered**  
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**  
Add any other context or screenshots about the feature request here.
