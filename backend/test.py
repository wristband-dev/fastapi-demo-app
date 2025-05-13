
import argparse


if __name__ == '__main__':
    # init parser
    parser = argparse.ArgumentParser(description='Run the FastAPI application')

    # add args
    parser.add_argument('--log-level', type=str, choices=[
            'DEBUG', 
            'INFO', 
            'WARNING', 
            'ERROR', 
            'CRITICAL'
        ],
        help='Set the logging level'
    )
    parser.add_argument('--debug', action='store_true', help='Set log level to DEBUG (overrides --log-level)')
    parser.add_argument('--host', type=str, help='Host to bind the server to')
    parser.add_argument('--port', type=int, help='Port to bind the server to')
    
    # parse args
    args = parser.parse_args()
    
    print(f"ARGS: {args}")