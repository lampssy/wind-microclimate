<div id="top"></div>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Tests][tests-shield]][tests-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">{{cookiecutter.name}}</h3>

  <p align="center">
    {{cookiecutter.description}}
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

Automated new project setup using GitHub Actions.

GitHub Actions execute:
* `cookiectter` for setting up the new repository
* `flake8` and `mypy` to check code styling
* `pytest` for testing
* `tox` for running tests in various environments

Steps to set up the project:
1. Click the big green button `Use this template` or click <a href="../../generate">here</a>.
2. Enter a Repository name and click `Create repository from template`
3. In the a new repository, <a href="../../edit/main/cookiecutter.json">complete the project setup</a> by editing the `cookiecutter.json` file. 
4. Hit <kbd>cmd</kbd> + <kbd>S</kbd> and then <kbd>Enter</kbd> to perform a commit (the commit message doesn't really matter).
5. Wait for <a href="../../actions">Setup Repository Action</a> to complete.

That's it, easy isn't it?

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [Next.js](https://nextjs.org/)
* [React.js](https://reactjs.org/)
* [Vue.js](https://vuejs.org/)
* [Angular](https://angular.io/)
* [Svelte](https://svelte.dev/)
* [Laravel](https://laravel.com)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

{{cookiecutter.author}} - {{cookiecutter.email}}

Project Link: [https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}](https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}})

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}.svg?
[contributors-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}.svg?
[forks-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/network/members
[stars-shield]: https://img.shields.io/github/stars/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}.svg?
[stars-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/stargazers
[issues-shield]: https://img.shields.io/github/issues/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}.svg?
[issues-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/issues
[license-shield]: https://img.shields.io/github/license/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}.svg?
[license-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/awownysz
[tests-shield]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/{{cookiecutter.user_name}}/{{cookiecutter.repo_name}}/actions/workflows/tests
[product-screenshot]: images/screenshot.png
