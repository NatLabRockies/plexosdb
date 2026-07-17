# Changelog

All notable changes to this project will be documented in this file.

## [1.6.0](https://github.com/NatLabRockies/plexosdb/compare/v1.5.0...v1.6.0) (2026-07-17)


### 🚀 Features

* add agentic skills guide for llms interactions ([#125](https://github.com/NatLabRockies/plexosdb/issues/125)) ([f8d6430](https://github.com/NatLabRockies/plexosdb/commit/f8d6430ac17345b421440e3da5d4e16096b51506))
* implement PLEXOS solution reader and setup master files for 9-12 versions ([#141](https://github.com/NatLabRockies/plexosdb/issues/141)) ([903cdcc](https://github.com/NatLabRockies/plexosdb/commit/903cdcca9cca9a98e6b8ac9c7473bfc4008b923d))
* MCP server integration ([#124](https://github.com/NatLabRockies/plexosdb/issues/124)) ([db1e77e](https://github.com/NatLabRockies/plexosdb/commit/db1e77e835e392d9e59c435248bc9d6c03fc3f9f))


### 📦 Build

* **deps-dev:** bump pytest from 9.0.2 to 9.0.3 ([#150](https://github.com/NatLabRockies/plexosdb/issues/150)) ([8e0b42f](https://github.com/NatLabRockies/plexosdb/commit/8e0b42f3300ac0d12aa85cd5acb71d3234739bf5))
* **deps-dev:** bump sphinx-autobuild from 2024.10.3 to 2025.8.25 ([#151](https://github.com/NatLabRockies/plexosdb/issues/151)) ([1502ee1](https://github.com/NatLabRockies/plexosdb/commit/1502ee11a26338e4fd1a59713037d7c74dc970ed))
* **deps:** bump actions/cache from 5.0.4 to 5.0.5 ([#147](https://github.com/NatLabRockies/plexosdb/issues/147)) ([82bef37](https://github.com/NatLabRockies/plexosdb/commit/82bef3718a167f1122d525934c58daec6f794ed8))
* **deps:** bump actions/labeler from 6.0.1 to 6.1.0 ([#146](https://github.com/NatLabRockies/plexosdb/issues/146)) ([60ffbdb](https://github.com/NatLabRockies/plexosdb/commit/60ffbdb6b4f53028701504bb339de5c338614be1))
* **deps:** bump benchmark-action/github-action-benchmark from 1.22.0 to 1.22.1 ([#149](https://github.com/NatLabRockies/plexosdb/issues/149)) ([4bb7b74](https://github.com/NatLabRockies/plexosdb/commit/4bb7b744dc193266aaa341b151e270c7f2cbb6b9))
* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([#148](https://github.com/NatLabRockies/plexosdb/issues/148)) ([d5df7d1](https://github.com/NatLabRockies/plexosdb/commit/d5df7d166008f47e52424354c318e223ca88f6a4))
* **deps:** bump peaceiris/actions-gh-pages from 4.0.0 to 4.1.0 ([#145](https://github.com/NatLabRockies/plexosdb/issues/145)) ([a5d2b26](https://github.com/NatLabRockies/plexosdb/commit/a5d2b26f64ea1d5ee050f594b8a82bdbb1e2c562))

## [1.5.0](https://github.com/NatLabRockies/plexosdb/compare/v1.4.1...v1.5.0) (2026-06-25)


### 🚀 Features

* add agent markdown for better integration call ([#142](https://github.com/NatLabRockies/plexosdb/issues/142)) ([3003e52](https://github.com/NatLabRockies/plexosdb/commit/3003e523aa916e3a52ea1c59743c60fef45f51c2))


### 🐛 Bug Fixes

* attributes ([#130](https://github.com/NatLabRockies/plexosdb/issues/130)) ([b4d276b](https://github.com/NatLabRockies/plexosdb/commit/b4d276bc1e0cb5ee8dbbdd6db534582c7bea10ce))

## [1.4.1](https://github.com/NatLabRockies/plexosdb/compare/v1.4.0...v1.4.1) (2026-05-22)

### 🐛 Bug Fixes

- copy_object date range metadata copying
  ([#143](https://github.com/NatLabRockies/plexosdb/issues/143))
  ([b60e5ad](https://github.com/NatLabRockies/plexosdb/commit/b60e5ad21032f05702ed74bb345f3f4579e2379d))

## [1.4.0](https://github.com/NatLabRockies/plexosdb/compare/v1.3.4...v1.4.0) (2026-05-21)

### 🚀 Features

- add new Purchaser enum for handling new type of loads
  ([#127](https://github.com/NatLabRockies/plexosdb/issues/127))
  ([c5d9a38](https://github.com/NatLabRockies/plexosdb/commit/c5d9a38e29ba929869c0194da4fddca3860bcc3c))
- address mixed issues
  ([#128](https://github.com/NatLabRockies/plexosdb/issues/128))
  ([eabaa5b](https://github.com/NatLabRockies/plexosdb/commit/eabaa5bdd80e3898a5ddb37aa082b4736f4579e9))

### 🐛 Bug Fixes

- add safe parsing for long int values
  ([#140](https://github.com/NatLabRockies/plexosdb/issues/140))
  ([c565313](https://github.com/NatLabRockies/plexosdb/commit/c565313d5b37839def642261ab05dd493ab1e879))
- resolve bug on add properties from records related methods
  ([#129](https://github.com/NatLabRockies/plexosdb/issues/129))
  ([b3f4dbb](https://github.com/NatLabRockies/plexosdb/commit/b3f4dbb5d85cb2077e0402b499fa929a67221df7))

### 📦 Build

- **deps-dev:** bump ipython from 9.8.0 to 9.13.0
  ([#137](https://github.com/NatLabRockies/plexosdb/issues/137))
  ([98c66d4](https://github.com/NatLabRockies/plexosdb/commit/98c66d4046183ae059e6bc4354913809f711e74a))
- **deps-dev:** bump sphinxcontrib-mermaid from 1.0.0 to 2.0.2
  ([#136](https://github.com/NatLabRockies/plexosdb/issues/136))
  ([8c26ac3](https://github.com/NatLabRockies/plexosdb/commit/8c26ac3ee0ffe32060d90b74d68745c3434117dd))
- **deps:** bump actions/upload-artifact from 7.0.0 to 7.0.1
  ([#121](https://github.com/NatLabRockies/plexosdb/issues/121))
  ([85194fe](https://github.com/NatLabRockies/plexosdb/commit/85194fec3d3c14f924ec0f33126271ceb0ec8524))
- **deps:** bump astral-sh/setup-uv from 7.6.0 to 8.1.0
  ([#122](https://github.com/NatLabRockies/plexosdb/issues/122))
  ([e189e14](https://github.com/NatLabRockies/plexosdb/commit/e189e146477ee75f38e70c473d0b612979ed787f))
- **deps:** bump benchmark-action/github-action-benchmark from 1.21.0 to 1.22.0
  ([#120](https://github.com/NatLabRockies/plexosdb/issues/120))
  ([4ac3c99](https://github.com/NatLabRockies/plexosdb/commit/4ac3c991fd18d703caceb68c38dc7556477d2385))
- **deps:** bump codecov/codecov-action from 5.5.3 to 6.0.0
  ([#118](https://github.com/NatLabRockies/plexosdb/issues/118))
  ([fc5c2e8](https://github.com/NatLabRockies/plexosdb/commit/fc5c2e8834f1932f960db3003a70d0a0dee9df87))
- **deps:** bump googleapis/release-please-action from 4.4.0 to 4.4.1
  ([#123](https://github.com/NatLabRockies/plexosdb/issues/123))
  ([8959d18](https://github.com/NatLabRockies/plexosdb/commit/8959d183c9872c450906af288148ba033d45b77f))

## [1.3.4](https://github.com/NatLabRockies/plexosdb/compare/v1.3.3...v1.3.4) (2026-03-27)

### 🧩 CI

- use release/v1 tag for pypa/gh-action-pypi-publish
  ([#107](https://github.com/NatLabRockies/plexosdb/issues/107))
  ([c4e58b8](https://github.com/NatLabRockies/plexosdb/commit/c4e58b8dc062f3302216b3caa7c9c6c1cc423c86))

### 📦 Build

- **deps:** bump actions/cache from 5.0.3 to 5.0.4
  ([#115](https://github.com/NatLabRockies/plexosdb/issues/115))
  ([1ff162a](https://github.com/NatLabRockies/plexosdb/commit/1ff162afe66dfe3bcad7d0dbb0a534b4a9d3374a))
- **deps:** bump astral-sh/setup-uv from 7.5.0 to 7.6.0
  ([#117](https://github.com/NatLabRockies/plexosdb/issues/117))
  ([13fb3cf](https://github.com/NatLabRockies/plexosdb/commit/13fb3cfb4c7a2affd7df504a2e152c9a2b0c1295))
- **deps:** bump astral-sh/setup-uv from
  b75dde52aef63a238519e7aecbbe79a4a52e4315 to
  e06108dd0aef18192324c70427afc47652e63a82
  ([#114](https://github.com/NatLabRockies/plexosdb/issues/114))
  ([96f3975](https://github.com/NatLabRockies/plexosdb/commit/96f397540b06e68e45075a5d700d2b0a91ebe112))
- **deps:** bump codecov/codecov-action from 5.5.2 to 5.5.3
  ([#116](https://github.com/NatLabRockies/plexosdb/issues/116))
  ([c86c8e2](https://github.com/NatLabRockies/plexosdb/commit/c86c8e254a85909043c8a7b25a10ff7d169d1e02))
- **deps:** bump googleapis/release-please-action from
  c3fc4de07084f75a2b61a5b933069bda6edf3d5c to
  16a9c90856f42705d54a6fda1823352bdc62cf38
  ([#112](https://github.com/NatLabRockies/plexosdb/issues/112))
  ([4150d56](https://github.com/NatLabRockies/plexosdb/commit/4150d56065f41cf916912daf9cda39281cf4e3df))
- **deps:** bump peaceiris/actions-gh-pages from
  e9c66a37f080288a11235e32cbe2dc5fb3a679cc to
  4f9cc6602d3f66b9c108549d475ec49e8ef4d45e
  ([#113](https://github.com/NatLabRockies/plexosdb/issues/113))
  ([c697f1d](https://github.com/NatLabRockies/plexosdb/commit/c697f1d7642dac4c16cd5ea9e11e327d684ff548))

## [1.3.3](https://github.com/NatLabRockies/plexosdb/compare/v1.3.2...v1.3.3) (2026-03-16)

### 🐛 Bug Fixes

- **ci:** harden all workflows per zizmor audit
  ([#105](https://github.com/NatLabRockies/plexosdb/issues/105))
  ([67ca845](https://github.com/NatLabRockies/plexosdb/commit/67ca84584d1e66410dc66b014a9b710a24b00b95))

### ⚡ Performance

- Improving performance of adding memberships from records
  ([#104](https://github.com/NatLabRockies/plexosdb/issues/104))
  ([1ea4a39](https://github.com/NatLabRockies/plexosdb/commit/1ea4a39612a1bef1a0f290eaeb40441874a2b8f0))

### 📦 Build

- **deps:** bump actions/download-artifact from 7 to 8
  ([#101](https://github.com/NatLabRockies/plexosdb/issues/101))
  ([0e572a0](https://github.com/NatLabRockies/plexosdb/commit/0e572a07a930f6e25f196e98fc879f65f7dd9daa))
- **deps:** bump actions/upload-artifact from 6 to 7
  ([#102](https://github.com/NatLabRockies/plexosdb/issues/102))
  ([22b8374](https://github.com/NatLabRockies/plexosdb/commit/22b8374aa7ed9d29eb36258a6a5ad16feb2e21c5))

## [1.3.2](https://github.com/NatLabRockies/plexosdb/compare/v1.3.1...v1.3.2) (2026-02-12)

### 🐛 Bug Fixes

- Add capability of having a system object name different than system
  ([#96](https://github.com/NatLabRockies/plexosdb/issues/96))
  ([6f3e408](https://github.com/NatLabRockies/plexosdb/commit/6f3e40827b2cc39445761a0822d31a58e4e7f126))
- Propagate `parent_class_enum` when it is not the system
  get_object_properties() and iterate_properties() reject valid properties when
  parent_class_enum is not System.
  ([#100](https://github.com/NatLabRockies/plexosdb/issues/100))
  ([7200897](https://github.com/NatLabRockies/plexosdb/commit/72008973493d086ba1901c6a4e88f3a68da135dd))

## [1.3.1](https://github.com/NatLabRockies/plexosdb/compare/v1.3.0...v1.3.1) (2026-02-10)

### 🐛 Bug Fixes

- copy_object and list_objects_by_class
  ([#90](https://github.com/NatLabRockies/plexosdb/issues/90))
  ([a11783e](https://github.com/NatLabRockies/plexosdb/commit/a11783edda469f5ad8f0dc6a5185139ce51fc1b7))

### 📦 Build

- **deps-dev:** bump ipython from 9.7.0 to 9.8.0
  ([#86](https://github.com/NatLabRockies/plexosdb/issues/86))
  ([50c97c5](https://github.com/NatLabRockies/plexosdb/commit/50c97c59e169860e9eace86dfaf0aeb62f795de2))
- **deps-dev:** bump pytest from 9.0.1 to 9.0.2
  ([#87](https://github.com/NatLabRockies/plexosdb/issues/87))
  ([07e697b](https://github.com/NatLabRockies/plexosdb/commit/07e697b6e142521e84394901e8360cf28d8b95d1))
- **deps:** bump actions/download-artifact from 6 to 7
  ([#89](https://github.com/NatLabRockies/plexosdb/issues/89))
  ([41ab2b4](https://github.com/NatLabRockies/plexosdb/commit/41ab2b47bbee8371aab0ca8a88a7dfcb5fa544d6))
- **deps:** bump actions/upload-artifact from 5 to 6
  ([#88](https://github.com/NatLabRockies/plexosdb/issues/88))
  ([fc840f8](https://github.com/NatLabRockies/plexosdb/commit/fc840f85991f803817a7910a09ca0ff06c6f4713))

## [1.3.0](https://github.com/NREL/plexosdb/compare/v1.2.2...v1.3.0) (2025-12-11)

### 🚀 Features

- Making add_from_records more robust
  ([#85](https://github.com/NREL/plexosdb/issues/85))
  ([827b2dd](https://github.com/NREL/plexosdb/commit/827b2ddaa24cd5c9531d4f78fab8f4e1cb441ff2))

### 📦 Build

- **deps:** bump pre-commit from 4.2.0 to 4.5.0
  ([#82](https://github.com/NREL/plexosdb/issues/82))
  ([a590ce9](https://github.com/NREL/plexosdb/commit/a590ce949bef17e8bfa81fe70bf75293d2e88aa8))
- **deps:** bump ruff from 0.14.7 to 0.14.8
  ([#83](https://github.com/NREL/plexosdb/issues/83))
  ([c4123e1](https://github.com/NREL/plexosdb/commit/c4123e13f38d43586e1ba306b09b7b73c04b7b59))

## [1.2.2](https://github.com/NREL/plexosdb/compare/v1.2.1...v1.2.2) (2025-12-06)

### 🐛 Bug Fixes

- Update battery collection enum naming and add increment to rank for same class
  enum ([#80](https://github.com/NREL/plexosdb/issues/80))
  ([e247e67](https://github.com/NREL/plexosdb/commit/e247e6731f05eeef792cf8de09f0123e6f9d2995))

## [1.2.1](https://github.com/NREL/plexosdb/compare/v1.2.0...v1.2.1) (2025-12-04)

### 🐛 Bug Fixes

- handle property related attributes on "add_properties_from_records" method
  ([#78](https://github.com/NREL/plexosdb/issues/78))
  ([1776d2a](https://github.com/NREL/plexosdb/commit/1776d2a614facef29d5a2a3df1f3a27dd154e359))

## [1.2.0](https://github.com/NREL/plexosdb/compare/v1.1.3...v1.2.0) (2025-12-02)

### 🚀 Features

- Adding method `add_datafile_tag` and refactor
  add_properties/add_properties_from_records
  ([#69](https://github.com/NREL/plexosdb/issues/69))
  ([1e6e018](https://github.com/NREL/plexosdb/commit/1e6e01852e46fba89b16120c07d472f4c84f94ab))
- Adding new fixtures for cleaner testing.
  ([#68](https://github.com/NREL/plexosdb/issues/68))
  ([9062baa](https://github.com/NREL/plexosdb/commit/9062baab8db1eb611dcb7364e952bbdb898fe36a))
- Adding query date_from and date_to to properties
  ([#67](https://github.com/NREL/plexosdb/issues/67))
  ([00d533b](https://github.com/NREL/plexosdb/commit/00d533b4b547822a09984cf59e40738fea330f4a))

### 🐛 Bug Fixes

- Adding new release-please workflow
  ([#71](https://github.com/NREL/plexosdb/issues/71))
  ([1f8da38](https://github.com/NREL/plexosdb/commit/1f8da384a9deb3edfa7a343e91999d3d37e07b17))

### 📦 Build

- **deps:** bump actions/checkout from 4 to 6
  ([#74](https://github.com/NREL/plexosdb/issues/74))
  ([bb7be8d](https://github.com/NREL/plexosdb/commit/bb7be8d0e36c332051ec1a1767b8862f4baec359))
- **deps:** bump actions/setup-python from 5 to 6
  ([#73](https://github.com/NREL/plexosdb/issues/73))
  ([18a0d9d](https://github.com/NREL/plexosdb/commit/18a0d9d26db2056d79bbdda6cec168e895abe0e9))
- **deps:** bump furo from 2024.8.6 to 2025.9.25
  ([#77](https://github.com/NREL/plexosdb/issues/77))
  ([3dd6463](https://github.com/NREL/plexosdb/commit/3dd64632666e31a38f6ed8f8bb15f9d333e64791))
- **deps:** bump ipython from 9.4.0 to 9.7.0
  ([#76](https://github.com/NREL/plexosdb/issues/76))
  ([ca687df](https://github.com/NREL/plexosdb/commit/ca687dfa466990e59c273c26908496c1fd5a8878))
- **deps:** bump pytest from 8.4.1 to 9.0.1
  ([#75](https://github.com/NREL/plexosdb/issues/75))
  ([5864d85](https://github.com/NREL/plexosdb/commit/5864d85e69e5e6cc865fc389e6b15f8e63785001))

## [0.0.1] - 2024-08-21

### 🐛 Bug Fixes

- _(get_memberships)_ Updated `get_membership` function (#6)

### ⚙️ Miscellaneous Tasks

- _(actions)_ Adding first version of GitHub actions (#5)
- _(actions)_ Fixing GitHub Actions and refactoring API (#7)
- Removing trailwhitespace

<!-- generated by git-cliff -->
