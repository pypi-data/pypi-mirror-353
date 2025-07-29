from xfit_rpa.core import XEngine, XApp, XPage, XModule, XAction


class LoginPage(XPage, register_name="sample01.login"):
    name = "sample01.login"
    description = "Sample01 Login Page"

    class LoginModule(XModule, register_name="sample01.login.login_form"):
        name = "login_form"
        description = "Sample01 Login Form"

        def _init_actions(self):
            self.add_action(
                XAction(
                    name="input_username",
                    action={type: 'fill'},
                    selector="#username",
                    default_params={"value": ""}
                )
            ).add_action(
                XAction(
                    name="input_password",
                    action="fill",
                    selector="#password",
                    default_params={"value": ""}
                )
            )


class Sample01App(XApp, register_name="sample01"):
    name = "sample01"


def main():
    # 从配置文件创建引擎
    from pathlib import Path
    engine = XEngine.from_config(Path('sample01.conf.yaml').resolve())
    engine.run_all()


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Done")
