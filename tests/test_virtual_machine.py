from hdk.virtual_machine.vm_start import run_virtual_machine


def test_translate_incorrect_program():
    run_result = run_virtual_machine()
    assert run_result == "Run"
