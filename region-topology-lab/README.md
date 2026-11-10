# Floor-plan Region Topology Lab

Review explicit orthogonal polygons for uncovered envelope area, multiple coverage, outside regions and the lengths of interfaces between exclusively occupied regions. Exact rational arithmetic keeps decimal drawing coordinates from turning a narrow gap into a tolerance-dependent guess.

The notebook contains five fully synthetic examples with SVG diagrams and exact reports. It includes a clean partition, a narrow gap, overlapping regions, an L-shaped region and a region extending outside the envelope. The CLI and tests use only Python's standard library.

```sh
python -m unittest -v test_topology
```

To audit your own trusted local annotation, use `python topology.py input.json` with `envelope` and `regions` matching the schema in `examples.json`. Coordinates must be integers or decimal strings, with one simple axis-aligned polygon per region. The polygon closes implicitly. Holes, diagonal edges, self-touching rings and automatic tracing from an image are outside this implementation. Coordinates are caller-supplied drawing units; the tool does not infer metres or measured floor area.

`multiply_covered_area` counts each overlapping cell once, even when three regions overlap. `exclusive_interfaces` measure interfaces between cells each occupied by exactly one different region. They do not identify physical walls, doors or access rights. An intentional open courtyard can be an uncovered area; a reported gap does not by itself prove a plan defect. The envelope and intended room definitions require human review.

This is a geometric annotation check, with no structural, survey, legal-title, accessibility or building-code conclusion. Repeated and invalid identifiers are rejected; malformed/oversized geometry is bounded. No source file is sent to an external service by the Python code. Public cloud notebooks should use synthetic examples and publish only inputs you intend to make public.

Maintained by [NovAsia Estate](https://novasia.estate/). Source and issues: [Open Property Lab](https://github.com/novasia-estate/open-property-lab/tree/main/region-topology-lab). MIT.
