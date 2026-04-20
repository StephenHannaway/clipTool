from clipboard_manager.main import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from clipboard-manager" in captured.out
