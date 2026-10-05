# Source verification — 2026-10-05

Only public documentation and repository metadata were fetched. No archive,
PCD, odometry, annotation file, or scientific output was downloaded or generated.

## Official release trail

- The [project download page](https://mixedsignalsdataset.cs.cornell.edu/download/)
  points to IEEE Dataport and the authors' devkit/code. The
  [authors' code repository](https://github.com/acfr/Mixed-Signals-Dataset)
  describes segment directories, per-agent PCDs and odometry, but its download
  placeholder is not a usable acquisition specification.
- The [author-maintained release card](https://huggingface.co/datasets/sberrio/Mixed-Signals-V2X)
  documents per-segment TARs, public labels in train, withheld validation/test
  labels, and `PointClouds/`, `Odometry/`, `labels/` members. Its competition
  labels use the top RSU frame. This is the proposed release for Valid Point.
- Read-only [release API](https://huggingface.co/api/datasets/sberrio/Mixed-Signals-V2X)
  returned revision `1a61aea747aa6bc45da2c2f085a1f1d3abc41f91` and last-modified
  `2026-07-08T06:25:30.000Z`. The
  [train tree API](https://huggingface.co/api/datasets/sberrio/Mixed-Signals-V2X/tree/main/train)
  returned 29 archive entries, including the following. A later intake must
  recheck this inventory at the pinned revision and hash downloaded content.

| Archive path | Published bytes | Published LFS SHA-256 (not locally verified) |
| --- | ---: | --- |
| `train/mini_7.tar` | 7894272000 | `46e9dbe9f6e952be9186a6271abbcaaf11c965a5589d785fc278afd3eb235663` |
| `train/mini_10.tar` | 7853803520 | `ba831ae3e82df52953f70929505faf3e8783b7dc588da7e9ccc5912feeb56a37` |
| `train/mini_11.tar` | 7763056640 | `c0ce489d33f7ee951edba2e811282b9c0069a054aa8c27e93a112d1ac6024ddf` |
| `train/mini_12.tar` | 7837788160 | `103fcd519b7284ee7690bddd86b68ce34d559f39d3a6ff8dc0a50b60e270eec0` |
| `train/mini_13.tar` | 7802398720 | `2d193aaed3b60cfeddd6197ac84b4034418e2e7013065e16320f5e04db3bd83a` |
| `train/mini_14.tar` | 7768442880 | `ffdb2c4d04a5debd628c511184262ca970879740743b5bfda88b21473e8471c8` |

Inventory verification is not content validation: labels may be missing for
some frames, transforms may need authoritative documentation, and native packet
arrival times are not established. Browser opening of the tree failed; the
public JSON API supplied the successful inventory check. No local raw archive
was inspected, and no claim is made about prior downloads in another project.

## Required future checks

Resolve author-published calibration and timing documentation via the
[official devkit](https://github.com/quan-dao/mixed-signals-devkit). Do not install
or import a detector stack. Record exact source revision and relevant field
definitions; independently implement the small reader and transforms only after
verification. Verify release license/access terms before acquisition. Missing
FOV/occlusion or arrival metadata stays unknown; point extrema are not a sensor
specification. Do not mix older JSON annotations and competition TXT labels
without a separately validated conversion and versioned adapter.
