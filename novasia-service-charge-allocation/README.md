# Service Charge Allocation

Allocate a quoted shared expense across explicit caller-defined weights without losing or inventing a minor currency unit. Largest remainders distribute the leftover units; ordinal IDs make ties deterministic regardless of input order. Exact quota fractions make each allocation explainable.

```csharp
using NovAsia.ServiceChargeAllocation;
var result = Allocator.Allocate(1001, "USD", new[] {
    new AllocationWeight("unit-a", 1m), new AllocationWeight("unit-b", 1m),
    new AllocationWeight("unit-c", 1m)
}); // 334,334,333 minor units; sum1001
```

For area-days, obtain the half-open overlap with `OverlapDays`, multiply that day count by your chosen area and supply the resulting weights. Vacancies, liability, tax and who must pay are your policy decisions. Overlapping ownership periods are not inferred or reconciled. A weight is not proof of an entitlement.

Currency is a three-letter label, not a changing ISO register lookup. You define its minor-unit precision. This API accepts nonnegative totals; credit notes need a separate caller policy. It performs no currency conversion, legal interpretation or allocation of responsibility.

## Build and verify

`.NET8+`: `dotnet run --project tests/Checks.csproj`; `dotnet pack -c Release`. The executable checks fixed thirds, decimal weights, permutation invariance, overflow, leap dates and reconciliation across30 group sizes. No external runtime dependencies.

Maintained by [NovAsia Estate](https://novasia.estate/). Source and issue reporting: [Open Property Lab](https://github.com/novasia-estate/open-property-lab/tree/main/novasia-service-charge-allocation). MIT licensed. Examples are synthetic arithmetic cases, not invoices or statutory rules.
