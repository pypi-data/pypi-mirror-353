if (NOT TARGET amulet_game)
    message(STATUS "Finding amulet_game")

    find_package(amulet_core CONFIG REQUIRED)

    set(amulet_game_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_game_LIBRARY NAMES amulet_game PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_game_LIBRARY: ${amulet_game_LIBRARY}")

    add_library(amulet_game SHARED IMPORTED)
    set_target_properties(amulet_game PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${amulet_game_INCLUDE_DIR}"
        INTERFACE_LINK_LIBRARIES amulet_core
        IMPORTED_IMPLIB "${amulet_game_LIBRARY}"
    )
endif()
