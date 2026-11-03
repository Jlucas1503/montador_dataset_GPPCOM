import contextlib
import io
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch


# Permite testar a CLI isoladamente mesmo antes da instalação de pandas/requests.
downloader = ModuleType("downloader")
downloader.listar_existentes = Mock()
downloader.obter_pasta_destino = Mock()
downloader.salvar_fotos = Mock()
sys.modules["downloader"] = downloader

inaturalist = ModuleType("inaturalist")
inaturalist.buscar_fotos = Mock()
inaturalist.buscar_taxon = Mock()
sys.modules["inaturalist"] = inaturalist

taxonomy = ModuleType("taxonomy")
taxonomy.carregar_especies = Mock()
taxonomy.limpar_nome = Mock()
sys.modules["taxonomy"] = taxonomy

import config
import main


class TestArgumentosCLI(unittest.TestCase):
    def test_le_especie_e_quantidade(self):
        argumentos = main.criar_parser().parse_args(
            ["--especie", "Callithrix jacchus", "--quantidade", "20"]
        )

        self.assertEqual(argumentos.especie, "Callithrix jacchus")
        self.assertEqual(argumentos.quantidade, 20)

    def test_rejeita_quantidade_invalida(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main.criar_parser().parse_args(["--quantidade", "0"])


class TestSelecaoDeRegistros(unittest.TestCase):
    def test_especie_direta_nao_le_csv(self):
        with patch.object(main, "carregar_especies") as carregar:
            registros = main.selecionar_registros("  Callithrix jacchus  ")

        self.assertEqual(
            registros, [{config.COL_ESPECIE: "Callithrix jacchus"}]
        )
        carregar.assert_not_called()

    def test_sem_especie_mantem_csv_como_fallback(self):
        dataframe = Mock()
        dataframe.to_dict.return_value = [{config.COL_ESPECIE: "Egretta thula"}]

        with patch.object(main, "carregar_especies", return_value=dataframe) as carregar:
            registros = main.selecionar_registros()

        self.assertEqual(registros, [{config.COL_ESPECIE: "Egretta thula"}])
        carregar.assert_called_once_with()
        dataframe.to_dict.assert_called_once_with(orient="records")

    def test_rejeita_nome_vazio(self):
        with self.assertRaisesRegex(ValueError, "não pode ficar vazio"):
            main.selecionar_registros("   ")


class TestProcessamento(unittest.TestCase):
    def test_quantidade_da_cli_chega_a_busca_de_fotos(self):
        registro = {config.COL_ESPECIE: "Callithrix jacchus"}

        with (
            patch.object(main, "selecionar_registros", return_value=[registro]),
            patch.object(
                main, "limpar_nome", return_value=("Callithrix jacchus", None)
            ),
            patch.object(main, "obter_pasta_destino", return_value=(Mock(), "nome")),
            patch.object(main, "listar_existentes", return_value=set()),
            patch.object(main, "buscar_taxon", return_value={"id": 42}),
            patch.object(main, "buscar_fotos", return_value=[]) as buscar_fotos,
            patch.object(main.time, "sleep"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            main.processar(especie="Callithrix jacchus", quantidade=7)

        buscar_fotos.assert_called_once_with(42, 7)


if __name__ == "__main__":
    unittest.main()
