#!/usr/bin/env python3


def run():
    command_bazel = "gcc -Wall -Wmissing-prototypes -Wpointer-arith -Wdeclaration-after-statement -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wimplicit-fallthrough=3 -Wcast-function-type -Wshadow=compatible-local -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-format-truncation -Wno-stringop-truncation -fvisibility=hidden -mavx pg_recvlogical.o  receivelog.o streamutil.o walmethods.o -L../../../src/port -L../../../src/common -L../../../src/fe_utils -lpgfeutils -L../../../src/interfaces/libpq -lpq -lstdc++  -Wl,--as-needed -Wl,-rpath,'/home/xiaochen/.cache/bazel/_bazel_xiaochen/def8392de60694faa9c9ea704dc32257/sandbox/processwrapper-sandbox/25/execroot/_main/bazel-out/k8-dbg/bin/postgres.build_tmpdir/postgres/lib',--enable-new-dtags  -lpgcommon -lpgport -lm  -o pg_recvlogical"

    command_native = "gcc -Wall -Wmissing-prototypes -Wpointer-arith -Wdeclaration-after-statement -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wimplicit-fallthrough=3 -Wcast-function-type -Wshadow=compatible-local -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-format-truncation -Wno-stringop-truncation -O2 pg_recvlogical.o  receivelog.o streamutil.o walmethods.o -L../../../src/port -L../../../src/common -L../../../src/fe_utils -lpgfeutils -L../../../src/interfaces/libpq -lpq   -Wl,--as-needed -Wl,-rpath,'/usr/local/pgsql/lib',--enable-new-dtags  -lpgcommon -lpgport -lm  -o pg_recvlogical"

    bazel_args = command_bazel.split()
    native_args = command_native.split()

    args_1, output_files_1 = dismentle_command(command_bazel)
    args_2, output_files_2 = dismentle_command(command_native)

    compare(args_1, "run with bazel", args_2, "run with native")
    compare(output_files_1, "run with bazel", output_files_2, "run with native")


def compare(group1: list[str], group1_name: str, group2: list[str], group2_name: str):
    print("common:")
    common_args = set(group1).intersection(set(group2))
    common_args = list(common_args)
    common_args.sort()
    for arg in common_args:
        print("\t" + arg)

    print(f"extra in ({group1_name}):")
    different_args = set(group1).difference(set(group2))
    different_args = list(different_args)
    different_args.sort()
    for arg in different_args:
        print("\t" + arg)

    print(f"extra in ({group2_name}):")
    different_args = set(group2).difference(set(group1))
    different_args = list(different_args)
    different_args.sort()
    for arg in different_args:
        print("\t" + arg)


# return tuple(args, output_files)
def dismentle_command(command: str) -> tuple[list[str], list[str]]:
    args = command.split()
    args = set(args)

    # remove entry "gcc"
    args.remove("gcc")

    output_files = set()
    for arg in args:
        if arg.startswith("-"):
            continue
        output_files.add(arg)
    for output_file in output_files:
        args.remove(output_file)

    args = list(args)
    args.sort()
    output_files = list(output_files)
    output_files.sort()

    return args, output_files


if __name__ == "__main__":
    run()
