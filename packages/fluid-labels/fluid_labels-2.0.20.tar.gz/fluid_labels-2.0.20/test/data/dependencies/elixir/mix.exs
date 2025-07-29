defmodule Mixup.Mixfile do
  use Mix.Project

  def project do
    [
      app: :mixup,
      version: "0.0.1",
      elixir: "~> 1.6.3",
      deps: deps(),
      build_embedded: Mix.env() == :prod,
      start_permanent: Mix.env() == :prod
    ]
  end

  def application do
    [applications: [:logger, :cowboy, :plug]]
  end

  defp deps do
    [
      {:poison, "~> 3.1.0"},
      {:plug, "~> 1.3.0"},
      {:coherence, "~> 0.5"},
      {:ecto, "~> 2.2.0", only: [:dev, :test]},
      {:inch_ex, "~> 1.0", only: :docs}
    ]
  end
end
