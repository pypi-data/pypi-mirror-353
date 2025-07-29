# minwei_tools

### This tools contain to major function

1. Dotter : Display animated text on screen during long missions
2. re_result : A Rust-like approach to error handling

# Install

```bash
pip install minwei_tools
```

# Usage

* ## Dotter

    ```python
    from minwei_tools import Dotter

    with Dotter(cycle = piano, message="Loading", delay=0.1, show_timer=1) as d:
        sleep(120)
    ```

* ## rs_result

    ```python
    from minwei_tools.rs_result import Result, Ok, Err

    def devide(a: int, b: int) -> Result[int, str]:
        if b == 0:
            return Err("Division by zero error")
        return Ok(a // b)

    result : Result[int, str] = devide(10, 0)
    match result:
        case Ok(value):
            print(f"Result: {value}")
        case Err(value):
            print(f"Error: {value}")
            
    result : Result[int, str] = devide(10, 2)
    match result:
        case Ok(value):
            print(f"Result: {value}")
        case Err(value):
            print(f"Error: {value}")
    ```