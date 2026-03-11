I'm working with a group of data scientists and we're trying to learn about how GitHub Actions work.

We'd like to create the most simple repo you can that describes how to make a minimal unit test suite run on merges to main. Please include manual instructions on how to configure the repo in the GitHub UI as well.

Requirements:
- use uv and python as your basic toolset
- for funtionality: build a tool that accepts an arbitrary dataframe from CSV and report on quality of columns and likely datatypes, and then propose a schema based on successful or failed typecasting attempts. For example, if a column is entirely filled with either NaN or integeters represented as strings, it would be a candidate to type cast to an int column.
- use ruff for linting, pydantic for schema generation
- use black with pre-commit
- provide comprehensive unit test suites, and make sure that they are called in github actions. Make sure to include a test that there's a tolerance for typecasting integers that doesn't exceed 1e-5. For example, you may decide to use np.is_close()
- describe your workflow and a "quick start" that optimizes learning opportunities about GH actions, and put all of this in the README.md. Any core topics you want to expand upon, put in separate .md files in a docs/ directory.
- For every file and every object, make sure to include a triple-quoted doc string that provides context to the developer.

Please ask me if you need any more feedback before starting.
