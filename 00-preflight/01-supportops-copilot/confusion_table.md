| Ticket | Actual Category | Zero-shot    | Detailed     | Few-shot     | Correct? |
| -----: | --------------- | ------------ | ------------ | ------------ | -------- |
|      1 | Billing         | Billing      | Billing      | Billing      | ✅        |
|      2 | Shipping        | Shipping     | Shipping     | Shipping     | ✅        |
|      3 | Account         | Account      | Account      | Account      | ✅        |
|      4 | Returns         | Returns      | Returns      | Returns      | ✅        |
|      5 | Shipping        | Shipping     | Shipping     | Shipping     | ✅        |
|      6 | Payment         | Payment      | Payment      | Payment      | ✅        |
|      7 | Returns         | Returns      | Returns      | Returns      | ✅        |
|      8 | Subscription    | Subscription | Subscription | Subscription | ✅        |
|      9 | Billing         | Billing      | Billing      | Billing      | ✅        |
|     10 | Account         | Account      | Account      | Account      | ✅        |


Prompt Comparison Summary

- Zero-shot correctly classified all 10 simple tickets.
- Detailed prompt also classified all tickets correctly.
- Few-shot produced the same results on this dataset.

Conclusion:
This dataset contains relatively straightforward support tickets. Therefore, all three prompting strategies achieved similar performance. On more ambiguous or complex tickets, Detailed and Few-shot prompting are generally expected to produce more consistent results because they provide additional guidance and examples.