"""
Command-line interface for Themis.
"""

import click


@click.group()
@click.version_option()
def cli():
    """Themis - AI Evaluation & Testing Framework."""
    pass


@cli.command()
@click.option('--input', '-i', help='Input text to evaluate')
@click.option('--evaluators', '-e', multiple=True, default=['hallucination'], 
              help='Evaluators to use')
def evaluate(input, evaluators):
    """Evaluate model output."""
    
    if not input:
        click.echo("Please provide input text with --input")
        return
    
    try:
        from themis import ThemisEvaluator, HallucinationDetector, BiasDetector
        
        # Initialize evaluator
        evaluator = ThemisEvaluator()
        
        # Add requested evaluators
        if 'hallucination' in evaluators:
            evaluator.add_evaluator(HallucinationDetector())
        if 'bias' in evaluators:
            evaluator.add_evaluator(BiasDetector())
        
        # Run evaluation
        results = evaluator.evaluate([input])
        
        # Display results
        click.echo("Evaluation Results:")
        click.echo("=" * 20)
        
        summary = results.summary()
        for key, value in summary.items():
            click.echo(f"{key}: {value}")
        
        for result in results.results:
            if result.success:
                click.echo(f"\n{result.evaluator_name}:")
                for metric, value in result.metrics.items():
                    if isinstance(value, float):
                        click.echo(f"  {metric}: {value:.3f}")
                    else:
                        click.echo(f"  {metric}: {value}")
        
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
def version():
    """Show version information."""
    try:
        import themis
        click.echo(f"Themis version: {themis.__version__}")
    except Exception as e:
        click.echo(f"Error getting version: {e}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
