-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 06-11-2025 a las 19:19:22
-- Versión del servidor: 10.4.14-MariaDB
-- Versión de PHP: 7.4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bienestar_universitario`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas`
--

CREATE TABLE `citas` (
  `ID_Cita` int(11) NOT NULL,
  `ID_Estudiante` int(11) NOT NULL,
  `ID_Psicologo` int(11) NOT NULL,
  `Fecha_Cita` date NOT NULL,
  `Hora_Cita` varchar(5) NOT NULL,
  `Estado_Cita` enum('SOLICITADA','CONFIRMADA','CANCELADA','REALIZADA') DEFAULT 'SOLICITADA',
  `Fecha_Solicitud` datetime DEFAULT current_timestamp(),
  `Nota_Ubicacion` varchar(255) DEFAULT 'Sede 4, Bloque G, Consultorio 1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `citas`
--

INSERT INTO `citas` (`ID_Cita`, `ID_Estudiante`, `ID_Psicologo`, `Fecha_Cita`, `Hora_Cita`, `Estado_Cita`, `Fecha_Solicitud`, `Nota_Ubicacion`) VALUES
(1, 1, 1, '2025-11-04', '07:00', 'CANCELADA', '2025-11-01 06:30:56', 'Sede 4, Bloque G, Consultorio 1'),
(25, 2, 1, '2025-11-03', '06:00', 'REALIZADA', '2025-11-01 06:34:05', 'awawawa'),
(26, 1, 1, '2025-11-03', '09:00', 'CANCELADA', '2025-11-01 06:34:46', 'Sede 4, Bloque G, Consultorio 1'),
(27, 1, 1, '2025-11-03', '09:00', 'CANCELADA', '2025-11-01 07:16:46', 'Sede 4, Bloque G, Consultorio 1'),
(28, 1, 1, '2025-11-03', '12:00', 'CANCELADA', '2025-11-01 17:31:46', 'Sede 4, Bloque G, Consultorio 1'),
(29, 1, 1, '2025-11-10', '12:00', 'CANCELADA', '2025-11-01 19:00:20', 'Sede 4, Bloque G, Consultorio 1'),
(30, 1, 1, '2025-11-03', '09:00', 'CANCELADA', '2025-11-02 01:31:57', 'Sede 4, Bloque G, Consultorio 1'),
(31, 1, 1, '2025-11-03', '09:00', 'CANCELADA', '2025-11-02 08:27:36', 'Sede 4, Bloque G, Consultorio 1'),
(32, 1, 1, '2025-11-10', '06:00', 'CANCELADA', '2025-11-02 08:33:14', 'Sede 4, Bloque G, Consultorio 1'),
(33, 1, 1, '2025-11-10', '06:00', 'REALIZADA', '2025-11-02 09:42:49', 'Sede 4, Bloque G, Consultorio 1zzzz'),
(34, 1, 1, '2025-11-03', '06:00', 'CANCELADA', '2025-11-02 12:19:21', 'Sede 4, Bloque G, Consultorio 1'),
(35, 1, 1, '2025-11-03', '06:00', 'CANCELADA', '2025-11-02 14:50:21', 'Sede 4, Bloque G, Consultorio 1'),
(36, 2, 1, '2025-11-03', '09:00', 'CONFIRMADA', '2025-11-02 15:34:08', 'Sede 4, Bloque G, Consultorio 1'),
(37, 1, 1, '2025-11-03', '06:00', 'CANCELADA', '2025-11-05 03:41:30', 'Sede 4, Bloque G, Consultorio 1'),
(38, 26, 1, '2025-11-03', '06:00', 'SOLICITADA', '2025-11-06 13:09:57', 'Sede 4, Bloque G, Consultorio 1');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `encuestas`
--

CREATE TABLE `encuestas` (
  `ID_Encuesta` int(11) NOT NULL,
  `ID_Cita` int(11) NOT NULL,
  `ID_Estudiante` int(11) NOT NULL,
  `Calificacion` int(11) NOT NULL COMMENT 'Puntaje de 1 a 5',
  `Comentario` text DEFAULT NULL,
  `Fecha_Respuesta` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `encuestas`
--

INSERT INTO `encuestas` (`ID_Encuesta`, `ID_Cita`, `ID_Estudiante`, `Calificacion`, `Comentario`, `Fecha_Respuesta`) VALUES
(1, 33, 1, 5, 'Cinco de Cinco', '2025-11-02 15:12:07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiantes`
--

CREATE TABLE `estudiantes` (
  `ID_Estudiante` int(11) NOT NULL,
  `ID_Usuario` int(11) NOT NULL,
  `Programa_Academico` varchar(100) NOT NULL,
  `Semestre` int(11) NOT NULL,
  `Telefono_Contacto` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `estudiantes`
--

INSERT INTO `estudiantes` (`ID_Estudiante`, `ID_Usuario`, `Programa_Academico`, `Semestre`, `Telefono_Contacto`) VALUES
(1, 1, 'Ingenieria', 3, '1122334455'),
(2, 3, 'fdfsdf', 6, '2141243'),
(15, 18, '', 0, ''),
(17, 20, '', 0, ''),
(24, 21, '', 0, ''),
(26, 22, 'Ing Sistemas', 6, '55994422');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `horarios_disponibles`
--

CREATE TABLE `horarios_disponibles` (
  `ID_Horario` int(11) NOT NULL,
  `ID_Psicologo` int(11) NOT NULL,
  `Dia_Semana` varchar(15) NOT NULL,
  `Hora_Inicio` varchar(5) NOT NULL,
  `Hora_Fin` varchar(5) NOT NULL,
  `Periodo_Academico` varchar(10) DEFAULT '2025-1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `horarios_disponibles`
--

INSERT INTO `horarios_disponibles` (`ID_Horario`, `ID_Psicologo`, `Dia_Semana`, `Hora_Inicio`, `Hora_Fin`, `Periodo_Academico`) VALUES
(17, 1, 'Lunes', '06:00', '09:00', '2025-1'),
(18, 1, 'Lunes', '09:00', '12:00', '2025-1'),
(19, 1, 'Lunes', '12:00', '15:00', '2025-1'),
(20, 1, 'Lunes', '15:00', '18:00', '2025-1'),
(21, 1, 'Lunes', '18:00', '21:00', '2025-1'),
(22, 1, 'Martes', '07:00', '10:00', '2025-1'),
(23, 1, 'Martes', '10:00', '13:00', '2025-1'),
(24, 1, 'Martes', '13:00', '16:00', '2025-1'),
(25, 1, 'Martes', '16:00', '19:00', '2025-1'),
(26, 1, 'Martes', '19:00', '22:00', '2025-1'),
(27, 1, 'Miércoles', '06:00', '09:00', '2025-1'),
(28, 1, 'Miércoles', '09:00', '12:00', '2025-1'),
(29, 1, 'Miércoles', '12:00', '15:00', '2025-1'),
(30, 1, 'Miércoles', '15:00', '18:00', '2025-1'),
(31, 1, 'Miércoles', '18:00', '21:00', '2025-1'),
(32, 1, 'Jueves', '07:00', '10:00', '2025-1'),
(33, 1, 'Jueves', '10:00', '13:00', '2025-1'),
(34, 1, 'Jueves', '13:00', '16:00', '2025-1'),
(35, 1, 'Jueves', '16:00', '19:00', '2025-1'),
(36, 1, 'Jueves', '19:00', '22:00', '2025-1'),
(37, 1, 'Viernes', '08:00', '11:00', '2025-1'),
(38, 1, 'Viernes', '11:00', '14:00', '2025-1'),
(39, 1, 'Viernes', '14:00', '17:00', '2025-1'),
(40, 1, 'Viernes', '17:00', '20:00', '2025-1'),
(41, 1, 'Sábado', '09:00', '12:00', '2025-1'),
(42, 1, 'Sábado', '12:00', '15:00', '2025-1'),
(43, 1, 'Sábado', '15:00', '18:00', '2025-1'),
(47, 1, 'Domingo', '06:00', '09:00', '2025-1');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `psicologos`
--

CREATE TABLE `psicologos` (
  `ID_Psicologo` int(11) NOT NULL,
  `ID_Usuario` int(11) NOT NULL,
  `Nombre_Completo_Display` varchar(200) NOT NULL,
  `Correo_Institucional` varchar(100) DEFAULT NULL,
  `Telefono_Contacto` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `psicologos`
--

INSERT INTO `psicologos` (`ID_Psicologo`, `ID_Usuario`, `Nombre_Completo_Display`, `Correo_Institucional`, `Telefono_Contacto`) VALUES
(1, 2, 'Psicologo 1', 'oficinapsicologia@hotmail.com', '00112233445566'),
(32, 1, 'DBTestN DBTestLN', 'psicologo-1@uni.edu', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `ID_Usuario` int(11) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Cedula` varchar(20) DEFAULT NULL,
  `Nombres` varchar(100) NOT NULL,
  `Apellidos` varchar(100) NOT NULL,
  `Rol` enum('Estudiante','Psicologo','Admin') DEFAULT 'Estudiante'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`ID_Usuario`, `Username`, `Password`, `Email`, `Cedula`, `Nombres`, `Apellidos`, `Rol`) VALUES
(1, 'DBTestU', '123456', 'dbtest1@hotmail.com', NULL, 'DBTestN', 'DBTestLN', 'Estudiante'),
(2, 'DBTestU2', '123456', 'dbtest2@hotmail.com', NULL, 'DBTestN2', 'DBTestLN2', 'Psicologo'),
(3, 'DBTestU3', '123456', 'dbtest3@hotmail.com', NULL, 'DBTestN3', 'DBTestLN3', 'Estudiante'),
(4, 'DBTestU4', '123456', 'dbtest4@hotmail.com', NULL, 'DBTestN4', 'DBTestLN4', 'Psicologo'),
(5, 'Admin', '123456', 'Admin@hotmail.com', NULL, 'AdminName', 'AdminLastName', 'Admin'),
(18, 'usuario', '123456', 'correo@hotmail.com', NULL, 'nombres', 'apellidos', 'Estudiante'),
(20, 'seguido', 'seguido', 'seguido@hotmail.com', NULL, 'seguido', 'seguido', 'Estudiante'),
(21, 'NuevoUsuarzzzio', '123456', 'NuevoUsuario@hotmail.com', NULL, 'Nombre', 'Apellidozzzz', 'Estudiante'),
(22, 'JuanPerez01', '123456', 'juanperez01@hotmail.com', '1090123456', 'Juan', 'Pérez', 'Estudiante');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `citas`
--
ALTER TABLE `citas`
  ADD PRIMARY KEY (`ID_Cita`),
  ADD KEY `ID_Estudiante` (`ID_Estudiante`),
  ADD KEY `ID_Psicologo` (`ID_Psicologo`);

--
-- Indices de la tabla `encuestas`
--
ALTER TABLE `encuestas`
  ADD PRIMARY KEY (`ID_Encuesta`),
  ADD UNIQUE KEY `ID_Cita_Unica` (`ID_Cita`),
  ADD KEY `FK_Encuesta_Estudiante` (`ID_Estudiante`);

--
-- Indices de la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  ADD PRIMARY KEY (`ID_Estudiante`),
  ADD UNIQUE KEY `ID_Usuario` (`ID_Usuario`);

--
-- Indices de la tabla `horarios_disponibles`
--
ALTER TABLE `horarios_disponibles`
  ADD PRIMARY KEY (`ID_Horario`),
  ADD KEY `ID_Psicologo` (`ID_Psicologo`);

--
-- Indices de la tabla `psicologos`
--
ALTER TABLE `psicologos`
  ADD PRIMARY KEY (`ID_Psicologo`),
  ADD UNIQUE KEY `ID_Usuario` (`ID_Usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`ID_Usuario`),
  ADD UNIQUE KEY `Username` (`Username`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD UNIQUE KEY `Cedula` (`Cedula`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `citas`
--
ALTER TABLE `citas`
  MODIFY `ID_Cita` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT de la tabla `encuestas`
--
ALTER TABLE `encuestas`
  MODIFY `ID_Encuesta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  MODIFY `ID_Estudiante` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT de la tabla `horarios_disponibles`
--
ALTER TABLE `horarios_disponibles`
  MODIFY `ID_Horario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT de la tabla `psicologos`
--
ALTER TABLE `psicologos`
  MODIFY `ID_Psicologo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `ID_Usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `citas`
--
ALTER TABLE `citas`
  ADD CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`ID_Estudiante`) REFERENCES `estudiantes` (`ID_Estudiante`),
  ADD CONSTRAINT `citas_ibfk_2` FOREIGN KEY (`ID_Psicologo`) REFERENCES `psicologos` (`ID_Psicologo`);

--
-- Filtros para la tabla `encuestas`
--
ALTER TABLE `encuestas`
  ADD CONSTRAINT `FK_Encuesta_Cita` FOREIGN KEY (`ID_Cita`) REFERENCES `citas` (`ID_Cita`),
  ADD CONSTRAINT `FK_Encuesta_Estudiante` FOREIGN KEY (`ID_Estudiante`) REFERENCES `estudiantes` (`ID_Estudiante`);

--
-- Filtros para la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  ADD CONSTRAINT `estudiantes_ibfk_1` FOREIGN KEY (`ID_Usuario`) REFERENCES `usuarios` (`ID_Usuario`);

--
-- Filtros para la tabla `horarios_disponibles`
--
ALTER TABLE `horarios_disponibles`
  ADD CONSTRAINT `horarios_disponibles_ibfk_1` FOREIGN KEY (`ID_Psicologo`) REFERENCES `psicologos` (`ID_Psicologo`);

--
-- Filtros para la tabla `psicologos`
--
ALTER TABLE `psicologos`
  ADD CONSTRAINT `psicologos_ibfk_1` FOREIGN KEY (`ID_Usuario`) REFERENCES `usuarios` (`ID_Usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
